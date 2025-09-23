#!/usr/bin/env python3
"""
Test Log Analyzer - Menganalisis log hasil testing yang tersimpan
"""
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import sys
from typing import List, Dict, Any
import pandas as pd


class TestLogAnalyzer:
    """Analyzer untuk log hasil testing"""
    
    def __init__(self, log_dir: Path = None):
        if log_dir is None:
            log_dir = Path("test_logs")
        
        self.log_dir = log_dir
        
        if not self.log_dir.exists():
            print(f"❌ Test log directory '{log_dir}' not found")
            sys.exit(1)
    
    def get_all_test_results(self) -> List[Dict[str, Any]]:
        """Get all test result files"""
        json_files = list(self.log_dir.glob("test_results_*.json"))
        results = []
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['log_file'] = str(json_file)
                    results.append(data)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"⚠️  Error reading {json_file}: {e}")
        
        # Sort by session start time
        results.sort(key=lambda x: x.get('session_start', ''), reverse=True)
        return results
    
    def show_recent_results(self, limit: int = 10):
        """Show recent test results"""
        results = self.get_all_test_results()
        
        if not results:
            print("📭 No test results found")
            return
        
        print(f"📊 Recent Test Results (Last {min(limit, len(results))} sessions)")
        print("=" * 80)
        
        for i, result in enumerate(results[:limit]):
            session_start = datetime.fromisoformat(result['session_start'])
            duration = result.get('total_duration', 0)
            summary = result.get('summary', {})
            
            success_rate = summary.get('success_rate', 0)
            status_icon = "✅" if success_rate == 100 else "❌" if success_rate == 0 else "⚠️"
            
            print(f"{i+1:2d}. {status_icon} {session_start.strftime('%Y-%m-%d %H:%M:%S')} "
                  f"| Duration: {duration:.1f}s | Success: {success_rate:.1f}%")
            
            # Show test run details
            for run in result.get('test_runs', []):
                run_status = "✅" if run['success'] else "❌"
                print(f"    {run_status} {run['test_type']}: {run['duration_seconds']:.2f}s")
        
        print("=" * 80)
    
    def show_test_statistics(self):
        """Show comprehensive test statistics"""
        results = self.get_all_test_results()
        
        if not results:
            print("📭 No test results found")
            return
        
        print("📈 Test Statistics Summary")
        print("=" * 60)
        
        # Overall statistics
        total_sessions = len(results)
        total_test_runs = sum(len(r.get('test_runs', [])) for r in results)
        
        # Success rates
        all_runs = []
        for result in results:
            all_runs.extend(result.get('test_runs', []))
        
        successful_runs = sum(1 for run in all_runs if run['success'])
        overall_success_rate = (successful_runs / len(all_runs) * 100) if all_runs else 0
        
        print(f"📊 Total Sessions: {total_sessions}")
        print(f"🧪 Total Test Runs: {total_test_runs}")
        print(f"✅ Successful Runs: {successful_runs}")
        print(f"❌ Failed Runs: {len(all_runs) - successful_runs}")
        print(f"📈 Overall Success Rate: {overall_success_rate:.1f}%")
        
        # Test type breakdown
        print(f"\n📋 Test Type Breakdown:")
        test_type_stats = {}
        for run in all_runs:
            test_type = run['test_type']
            if test_type not in test_type_stats:
                test_type_stats[test_type] = {'total': 0, 'success': 0}
            
            test_type_stats[test_type]['total'] += 1
            if run['success']:
                test_type_stats[test_type]['success'] += 1
        
        for test_type, stats in test_type_stats.items():
            success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {test_type}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Duration statistics
        durations = [run['duration_seconds'] for run in all_runs]
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            
            print(f"\n⏱️  Duration Statistics:")
            print(f"  Average: {avg_duration:.2f}s")
            print(f"  Maximum: {max_duration:.2f}s")
            print(f"  Minimum: {min_duration:.2f}s")
        
        print("=" * 60)
    
    def show_failure_analysis(self):
        """Analyze test failures"""
        results = self.get_all_test_results()
        
        if not results:
            print("📭 No test results found")
            return
        
        print("🔍 Failure Analysis")
        print("=" * 60)
        
        # Collect all failed runs
        failed_runs = []
        for result in results:
            for run in result.get('test_runs', []):
                if not run['success']:
                    run['session_date'] = result['session_start']
                    failed_runs.append(run)
        
        if not failed_runs:
            print("🎉 No test failures found!")
            return
        
        # Group by test type
        failure_by_type = {}
        for run in failed_runs:
            test_type = run['test_type']
            if test_type not in failure_by_type:
                failure_by_type[test_type] = []
            failure_by_type[test_type].append(run)
        
        for test_type, failures in failure_by_type.items():
            print(f"\n❌ {test_type} Failures ({len(failures)}):")
            
            # Show recent failures
            recent_failures = sorted(failures, key=lambda x: x['session_date'], reverse=True)[:5]
            
            for failure in recent_failures:
                session_date = datetime.fromisoformat(failure['session_date'])
                print(f"  • {session_date.strftime('%Y-%m-%d %H:%M')} - "
                      f"Return code: {failure['return_code']}, "
                      f"Duration: {failure['duration_seconds']:.2f}s")
        
        print("=" * 60)
    
    def export_to_csv(self, output_file: str = None):
        """Export test results to CSV"""
        results = self.get_all_test_results()
        
        if not results:
            print("📭 No test results to export")
            return
        
        # Flatten data for CSV
        rows = []
        for result in results:
            session_start = result['session_start']
            session_duration = result.get('total_duration', 0)
            
            for run in result.get('test_runs', []):
                rows.append({
                    'session_start': session_start,
                    'session_duration': session_duration,
                    'test_type': run['test_type'],
                    'success': run['success'],
                    'return_code': run['return_code'],
                    'duration_seconds': run['duration_seconds'],
                    'timestamp': run['timestamp'],
                    'tests_collected': run.get('tests_collected', 0),
                    'tests_passed': run.get('tests_passed', 0),
                    'tests_failed': run.get('tests_failed', 0),
                    'warnings': run.get('warnings', 0)
                })
        
        # Create DataFrame and export
        df = pd.DataFrame(rows)
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"test_analysis_{timestamp}.csv"
        
        df.to_csv(output_file, index=False)
        print(f"📊 Exported {len(rows)} test records to {output_file}")
    
    def show_trends(self, days: int = 7):
        """Show test trends over time"""
        results = self.get_all_test_results()
        
        if not results:
            print("📭 No test results found")
            return
        
        # Filter results by time period
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_results = [
            r for r in results 
            if datetime.fromisoformat(r['session_start']) >= cutoff_date
        ]
        
        if not recent_results:
            print(f"📭 No test results found in the last {days} days")
            return
        
        print(f"📈 Test Trends (Last {days} days)")
        print("=" * 60)
        
        # Daily breakdown
        daily_stats = {}
        for result in recent_results:
            date_key = datetime.fromisoformat(result['session_start']).date()
            
            if date_key not in daily_stats:
                daily_stats[date_key] = {'sessions': 0, 'success_rate': []}
            
            daily_stats[date_key]['sessions'] += 1
            summary = result.get('summary', {})
            if 'success_rate' in summary:
                daily_stats[date_key]['success_rate'].append(summary['success_rate'])
        
        for date, stats in sorted(daily_stats.items()):
            avg_success_rate = sum(stats['success_rate']) / len(stats['success_rate']) if stats['success_rate'] else 0
            status_icon = "✅" if avg_success_rate == 100 else "❌" if avg_success_rate == 0 else "⚠️"
            
            print(f"{date} {status_icon}: {stats['sessions']} sessions, "
                  f"avg success rate: {avg_success_rate:.1f}%")
        
        print("=" * 60)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test Log Analyzer")
    parser.add_argument("--recent", type=int, default=10, help="Show recent test results")
    parser.add_argument("--stats", action="store_true", help="Show comprehensive statistics")
    parser.add_argument("--failures", action="store_true", help="Analyze test failures")
    parser.add_argument("--trends", type=int, metavar="DAYS", help="Show trends over N days")
    parser.add_argument("--export", type=str, metavar="FILE", help="Export to CSV file")
    parser.add_argument("--log-dir", type=str, help="Test log directory path")
    
    args = parser.parse_args()
    
    # Initialize analyzer
    log_dir = Path(args.log_dir) if args.log_dir else Path("test_logs")
    analyzer = TestLogAnalyzer(log_dir)
    
    # Execute requested analysis
    if args.stats:
        analyzer.show_test_statistics()
    elif args.failures:
        analyzer.show_failure_analysis()
    elif args.trends:
        analyzer.show_trends(args.trends)
    elif args.export:
        try:
            import pandas as pd
            analyzer.export_to_csv(args.export)
        except ImportError:
            print("❌ pandas is required for CSV export. Install with: pip install pandas")
            return 1
    else:
        # Default: show recent results
        analyzer.show_recent_results(args.recent)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())