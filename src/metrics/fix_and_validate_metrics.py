#!/usr/bin/env python3
"""
Metrics Recovery and Validation Tool

This tool recovers JSON data from CSV and validates the metrics system.
"""

import csv
import json
from pathlib import Path
from datetime import datetime
import sys
import os

# Add src to path to import our modules  
sys.path.append(str(Path(__file__).parent.parent))

def recover_json_from_csv():
    """Recover JSON data from CSV file"""
    csv_file = Path("execution_metrics/execution_metrics.csv")
    json_file = Path("execution_metrics/execution_metrics.json")
    
    print("[INFO] Recovering JSON data from CSV...")
    
    if not csv_file.exists():
        print("[FAIL] CSV file not found!")
        return False
    
    try:
        # Read CSV data
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"[CHART] Found {len(rows)} records in CSV")
        
        # Convert to JSON format
        executions = []
        for row in rows:
            # Convert string numbers back to proper types
            execution = {}
            for key, value in row.items():
                if key in ['duration_seconds', 'duration_minutes', 'success_rate', 'rows_per_second', 'avg_batch_processing_time']:
                    try:
                        execution[key] = float(value) if value else 0.0
                    except ValueError:
                        execution[key] = 0.0
                elif key in ['total_rows', 'processed_rows', 'failed_rows', 'batch_count', 'batch_size']:
                    try:
                        execution[key] = int(value) if value else 0
                    except ValueError:
                        execution[key] = 0
                else:
                    execution[key] = value
            
            executions.append(execution)
        
        # Save to JSON
        json_data = {"executions": executions}
        
        # Create backup of existing JSON if it exists
        if json_file.exists():
            backup_file = json_file.with_suffix('.json.backup')
            # Remove existing backup if present
            if backup_file.exists():
                backup_file.unlink()
            json_file.rename(backup_file)
            print(f"[INFO] Backed up existing JSON to {backup_file}")
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Successfully recovered {len(executions)} executions to JSON")
        return True
        
    except Exception as e:
        print(f"[FAIL] Error recovering data: {e}")
        return False

def validate_metrics_system():
    """Validate that the metrics system is working correctly"""
    print("\n[SEARCH] Validating metrics system...")
    
    try:
        from metrics.metrics_tracker import ExecutionMetricsTracker
        from metrics.metrics_visualizer import MetricsVisualizer
        
        # Test metrics tracker
        tracker = ExecutionMetricsTracker()
        print("[OK] MetricsTracker imported successfully")
        
        # Test getting summary
        summary = tracker.get_metrics_summary(days=30)
        if "error" not in summary:
            print(f"[OK] Summary generated: {summary.get('total_executions', 0)} executions found")
        else:
            print(f"[WARNING]  Summary warning: {summary['error']}")
        
        # Test visualizer
        visualizer = MetricsVisualizer()
        print("[OK] MetricsVisualizer imported successfully")
        
        # Test loading data
        try:
            df = visualizer.load_data()
            print(f"[OK] Data loaded: {len(df)} valid records")
            
            # Test basic analysis
            if len(df) >= 2:
                print("[OK] Sufficient data for analysis")
                
                # Show basic stats
                avg_duration = df['duration_seconds'].mean()
                avg_success = df['success_rate'].mean()
                total_processed = df['processed_rows'].sum()
                
                print(f"[CHART] Avg Duration: {avg_duration:.1f}s")
                print(f"[CHART] Avg Success Rate: {avg_success:.1f}%")
                print(f"[CHART] Total Rows Processed: {total_processed:,}")
            else:
                print("[WARNING]  Limited data for full analysis")
                
        except Exception as load_error:
            print(f"[FAIL] Data loading error: {load_error}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Validation error: {e}")
        return False

def test_metrics_integration():
    """Test integration with main system"""
    print("\n[TEST] Testing metrics integration...")
    
    try:
        from metrics.metrics_tracker import ExecutionMetricsTracker
        
        # Test creating a mock session
        tracker = ExecutionMetricsTracker()
        
        # Simulate a session
        session_id = tracker.start_session("test_dataset.xlsx", 100, 10)
        print(f"[OK] Session started: {session_id}")
        
        # Update progress
        tracker.update_progress(processed_rows=50, failed_rows=5, batch_count=5)
        print("[OK] Progress updated")
        
        # End session (but don't save to avoid corrupting real data)
        # Just test the logic without saving
        if hasattr(tracker, 'session_data') and tracker.session_data:
            print("[OK] Session data structure valid")
            print(f"   Processed rows: {tracker.session_data.get('processed_rows', 0)}")
            print(f"   Success rate: {tracker.session_data.get('success_rate', 0):.1f}%")
        
        # Reset without saving
        tracker.session_id = None
        tracker.start_time = None
        tracker.session_data = {}
        
        print("[OK] Metrics integration test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Integration test failed: {e}")
        return False

def create_analysis_script():
    """Create a unified analysis script"""
    script_content = '''#!/usr/bin/env python3
"""
Unified Metrics Analysis Tool

Provides comprehensive analysis of execution metrics including:
- Summary statistics
- Performance trends  
- Visualization generation
- Data export capabilities
"""

import sys
from pathlib import Path
import argparse

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    parser = argparse.ArgumentParser(description="Analyze execution metrics")
    parser.add_argument("command", choices=["summary", "trends", "visualize", "export", "all"],
                       help="Analysis command to run")
    parser.add_argument("--days", type=int, default=30, help="Days of data to analyze")
    parser.add_argument("--show", action="store_true", help="Show plots instead of saving")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    try:
        from metrics.metrics_tracker import ExecutionMetricsTracker
        from metrics.metrics_visualizer import MetricsVisualizer
        
        tracker = ExecutionMetricsTracker()
        visualizer = MetricsVisualizer()
        
        if args.command == "summary":
            summary = tracker.get_metrics_summary(days=args.days)
            print_summary(summary)
            
        elif args.command == "trends":
            try:
                plot_file = visualizer.create_performance_trends(save_plot=not args.show)
                if plot_file:
                    print(f"[CHART] Trends plot saved: {plot_file}")
                else:
                    print("[CHART] Trends plot displayed")
            except Exception as e:
                print(f"[FAIL] Error creating trends: {e}")
                
        elif args.command == "visualize":
            try:
                plot_file = visualizer.create_duration_vs_rows_scatter(save_plot=not args.show)
                if plot_file:
                    print(f"[CHART] Scatter plot saved: {plot_file}")
                else:
                    print("[CHART] Scatter plot displayed")
            except Exception as e:
                print(f"[FAIL] Error creating visualization: {e}")
                
        elif args.command == "export":
            output_file = args.output or f"metrics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            try:
                export_file = tracker.export_for_analysis(output_file)
                print(f"[CHART] Data exported: {export_file}")
            except Exception as e:
                print(f"[FAIL] Export error: {e}")
                
        elif args.command == "all":
            print("[CHART] Comprehensive Analysis\\n")
            
            # Summary
            summary = tracker.get_metrics_summary(days=args.days)
            print_summary(summary)
            
            # Visualizations
            try:
                scatter_file = visualizer.create_duration_vs_rows_scatter(save_plot=True)
                print(f"\\n[CHART] Scatter plot: {scatter_file}")
            except Exception as e:
                print(f"\\n[FAIL] Scatter plot error: {e}")
                
            try:
                trends_file = visualizer.create_performance_trends(save_plot=True)
                print(f"[CHART] Trends plot: {trends_file}")
            except Exception as e:
                print(f"[FAIL] Trends plot error: {e}")
            
            # Export
            try:
                export_file = tracker.export_for_analysis()
                print(f"[CHART] Export file: {export_file}")
            except Exception as e:
                print(f"[FAIL] Export error: {e}")
                
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        print("[TIP] Make sure you're running from the project root directory")
        
    except Exception as e:
        print(f"[FAIL] Analysis error: {e}")

def print_summary(summary):
    """Print formatted summary"""
    if "error" in summary:
        print(f"[FAIL] {summary['error']}")
        return
        
    print("="*60)
    print("[CHART] EXECUTION METRICS SUMMARY")
    print("="*60)
    print(f"[DATE] Period: Last {summary.get('period_days', 30)} days")
    print(f"[TEST] Total executions: {summary.get('total_executions', 0)}")
    print(f"[TIME]  Average duration: {summary.get('avg_duration_seconds', 0):.2f} seconds")
    print(f"[GRAPH] Duration range: {summary.get('min_duration_seconds', 0):.2f}s - {summary.get('max_duration_seconds', 0):.2f}s")
    print(f"[LIST] Average rows processed: {summary.get('avg_rows_processed', 0):.0f}")
    print(f"[CHART] Rows range: {summary.get('min_rows_processed', 0)} - {summary.get('max_rows_processed', 0):,}")
    print(f"[OK] Average success rate: {summary.get('avg_success_rate', 0):.1f}%")
    print(f"[TARGET] Total rows processed: {summary.get('total_rows_processed', 0):,}")

if __name__ == "__main__":
    from datetime import datetime
    main()
'''
    
    script_file = Path("analyze_metrics.py")
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"[OK] Analysis script created: {script_file}")
    return script_file

def main():
    print("METRICS SYSTEM RECOVERY & VALIDATION")
    print("="*50)
    
    # Step 1: Recover JSON from CSV
    if recover_json_from_csv():
        print("[OK] JSON recovery completed")
    else:
        print("[FAIL] JSON recovery failed")
        return
    
    # Step 2: Validate metrics system
    if validate_metrics_system():
        print("[OK] Metrics system validation passed")
    else:
        print("[FAIL] Metrics system validation failed")
        return
    
    # Step 3: Test integration
    if test_metrics_integration():
        print("[OK] Integration test passed")
    else:
        print("[FAIL] Integration test failed")
        return
    
    # Step 4: Create analysis script
    analysis_script = create_analysis_script()
    
    print("\n[SUCCESS] METRICS SYSTEM READY!")
    print("="*30)
    print("[CHART] Available commands:")
    print(f"   python {analysis_script} summary")
    print(f"   python {analysis_script} trends")  
    print(f"   python {analysis_script} visualize")
    print(f"   python {analysis_script} export")
    print(f"   python {analysis_script} all")
    print()
    print("[TIP] Example usage:")
    print(f"   python {analysis_script} summary --days 7")
    print(f"   python {analysis_script} visualize --show")
    print(f"   python {analysis_script} all")

if __name__ == "__main__":
    main()