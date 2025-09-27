#!/usr/bin/env python3
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
sys.path.append(str(Path(__file__).parent.parent))

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
                    print(f"[INFO] Trends plot saved: {plot_file}")
                else:
                    print("[INFO] Trends plot displayed")
            except Exception as e:
                print(f"[ERROR] Error creating trends: {e}")
                
        elif args.command == "visualize":
            try:
                plot_file = visualizer.create_duration_vs_rows_scatter(save_plot=not args.show)
                if plot_file:
                    print(f"[INFO] Scatter plot saved: {plot_file}")
                else:
                    print("[INFO] Scatter plot displayed")
            except Exception as e:
                print(f"[ERROR] Error creating visualization: {e}")
                
        elif args.command == "export":
            output_file = args.output or f"metrics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            try:
                export_file = tracker.export_for_analysis(output_file)
                print(f"[INFO] Data exported: {export_file}")
            except Exception as e:
                print(f"[ERROR] Export error: {e}")
                
        elif args.command == "all":
            print("[INFO] Comprehensive Analysis\n")
            
            # Summary
            summary = tracker.get_metrics_summary(days=args.days)
            print_summary(summary)
            
            # Visualizations
            try:
                scatter_file = visualizer.create_duration_vs_rows_scatter(save_plot=True)
                print(f"\n[INFO] Scatter plot: {scatter_file}")
            except Exception as e:
                print(f"\n[ERROR] Scatter plot error: {e}")
                
            try:
                trends_file = visualizer.create_performance_trends(save_plot=True)
                print(f"[INFO] Trends plot: {trends_file}")
            except Exception as e:
                print(f"[ERROR] Trends plot error: {e}")
            
            # Export
            try:
                export_file = tracker.export_for_analysis()
                print(f"[INFO] Export file: {export_file}")
            except Exception as e:
                print(f"[ERROR] Export error: {e}")
                
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        print("[TIP] Make sure you're running from the project root directory")
        
    except Exception as e:
        print(f"[ERROR] Analysis error: {e}")

def print_summary(summary):
    """Print formatted summary"""
    if "error" in summary:
        print(f"[ERROR] {summary['error']}")
        return
        
    print("="*60)
    print("EXECUTION METRICS SUMMARY")
    print("="*60)
    print(f"Period: Last {summary.get('period_days', 30)} days")
    print(f"Total executions: {summary.get('total_executions', 0)}")
    print(f"Average duration: {summary.get('avg_duration_seconds', 0):.2f} seconds")
    print(f"Duration range: {summary.get('min_duration_seconds', 0):.2f}s - {summary.get('max_duration_seconds', 0):.2f}s")
    print(f"Average rows processed: {summary.get('avg_rows_processed', 0):.0f}")
    print(f"Rows range: {summary.get('min_rows_processed', 0)} - {summary.get('max_rows_processed', 0):,}")
    print(f"Average success rate: {summary.get('avg_success_rate', 0):.1f}%")
    print(f"Total rows processed: {summary.get('total_rows_processed', 0):,}")

if __name__ == "__main__":
    from datetime import datetime
    main()
