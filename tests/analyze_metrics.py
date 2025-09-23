#!/usr/bin/env python3
"""
Execution Metrics Analysis CLI Tool

This tool provides command-line interface for analyzing execution metrics,
generating visualizations, and creating performance reports.
"""

import argparse
import sys
from pathlib import Path
import logging

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from core_logic.metrics_tracker import ExecutionMetricsTracker
    from core_logic.metrics_visualizer import MetricsVisualizer
except ImportError as e:
    print(f"ERROR: Failed to import required modules: {e}")
    print("Please ensure you're running this from the project root directory.")
    sys.exit(1)

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)-8s - %(message)s'
    )

def cmd_summary(args):
    """Show summary of recent execution metrics."""
    try:
        tracker = ExecutionMetricsTracker(args.metrics_dir)
        summary = tracker.get_metrics_summary(days=args.days)
        
        if "error" in summary:
            print(f"❌ {summary['error']}")
            return
        
        print("📊 EXECUTION METRICS SUMMARY")
        print("=" * 50)
        print(f"📅 Period: Last {summary['period_days']} days")
        print(f"🧪 Total executions: {summary['total_executions']}")
        print(f"⏱️  Average duration: {summary['avg_duration_seconds']:.2f} seconds")
        print(f"📈 Duration range: {summary['min_duration_seconds']:.2f}s - {summary['max_duration_seconds']:.2f}s")
        print(f"📋 Average rows processed: {summary['avg_rows_processed']:.0f}")
        print(f"📊 Rows range: {summary['min_rows_processed']} - {summary['max_rows_processed']}")
        print(f"✅ Average success rate: {summary['avg_success_rate']:.1f}%")
        print(f"🎯 Total rows processed: {summary['total_rows_processed']}")
        
    except Exception as e:
        print(f"❌ Failed to generate summary: {e}")

def cmd_scatter(args):
    """Generate scatter plot of duration vs rows."""
    try:
        visualizer = MetricsVisualizer(args.metrics_dir)
        plot_path = visualizer.create_duration_vs_rows_scatter(save_plot=not args.show)
        
        if plot_path:
            print(f"📈 Scatter plot saved: {plot_path}")
        else:
            print("📈 Scatter plot displayed")
            
    except Exception as e:
        print(f"❌ Failed to create scatter plot: {e}")

def cmd_trends(args):
    """Generate performance trends chart."""
    try:
        visualizer = MetricsVisualizer(args.metrics_dir)
        plot_path = visualizer.create_performance_trends(save_plot=not args.show)
        
        if plot_path:
            print(f"📈 Trends chart saved: {plot_path}")
        else:
            print("📈 Trends chart displayed")
            
    except Exception as e:
        print(f"❌ Failed to create trends chart: {e}")

def cmd_analysis(args):
    """Generate comprehensive analysis dashboard."""
    try:
        visualizer = MetricsVisualizer(args.metrics_dir)
        plots = visualizer.create_comprehensive_analysis(save_plot=True)
        
        print("📊 COMPREHENSIVE ANALYSIS COMPLETE")
        print("=" * 50)
        for plot_type, plot_path in plots.items():
            if plot_path:
                print(f"📈 {plot_type.capitalize()}: {plot_path}")
        
        # Also generate regression analysis
        regression = visualizer.get_regression_analysis()
        print(f"\n🔍 REGRESSION ANALYSIS")
        print(f"📐 Equation: {regression['model']['equation']}")
        print(f"📊 R²: {regression['statistics']['r_squared']:.4f}")
        print(f"🔗 Correlation: {regression['statistics']['correlation']:.4f}")
        print(f"📋 Data points: {regression['statistics']['data_points']}")
        
        print(f"\n🔮 PREDICTIONS:")
        for rows, duration in regression['predictions'].items():
            print(f"   {rows}: {duration:.2f} seconds")
            
    except Exception as e:
        print(f"❌ Failed to create analysis: {e}")

def cmd_regression(args):
    """Show detailed regression analysis."""
    try:
        visualizer = MetricsVisualizer(args.metrics_dir)
        analysis = visualizer.get_regression_analysis()
        
        print("🔍 REGRESSION ANALYSIS")
        print("=" * 50)
        
        model = analysis['model']
        stats = analysis['statistics']
        predictions = analysis['predictions']
        
        print(f"📐 Linear Equation:")
        print(f"   {model['equation']}")
        print(f"\n📊 Statistics:")
        print(f"   R² (coefficient of determination): {stats['r_squared']:.6f}")
        print(f"   Correlation coefficient: {stats['correlation']:.6f}")
        print(f"   Data points: {stats['data_points']}")
        print(f"   Mean duration: {stats['mean_duration']:.2f} seconds")
        print(f"   Mean rows: {stats['mean_rows']:.0f}")
        
        print(f"\n🔮 Duration Predictions:")
        for rows, duration in predictions.items():
            print(f"   {rows.replace('_', ' ').title()}: {duration:.2f} seconds")
        
        print(f"\n💡 Interpretation:")
        r2 = stats['r_squared']
        if r2 > 0.8:
            print("   🟢 Strong linear relationship - Duration scales predictably with row count")
        elif r2 > 0.5:
            print("   🟡 Moderate linear relationship - Row count partially explains duration")
        else:
            print("   🔴 Weak linear relationship - Other factors significantly affect duration")
            
    except Exception as e:
        print(f"❌ Failed to generate regression analysis: {e}")

def cmd_report(args):
    """Generate comprehensive text report."""
    try:
        visualizer = MetricsVisualizer(args.metrics_dir)
        report_path = visualizer.generate_report(args.output)
        
        print(f"📋 Comprehensive report generated: {report_path}")
        
        # Also display key insights
        if not args.output or not args.quiet:
            analysis = visualizer.get_regression_analysis()
            print(f"\n🎯 KEY INSIGHTS:")
            print(f"   • Linear equation: {analysis['model']['equation']}")
            print(f"   • R² = {analysis['statistics']['r_squared']:.4f} (explains {analysis['statistics']['r_squared']*100:.1f}% of variance)")
            print(f"   • Processing 1000 rows typically takes: {analysis['predictions']['1000_rows']:.2f} seconds")
            
    except Exception as e:
        print(f"❌ Failed to generate report: {e}")

def cmd_export(args):
    """Export metrics data for external analysis."""
    try:
        tracker = ExecutionMetricsTracker(args.metrics_dir)
        export_path = tracker.export_for_analysis(args.output)
        
        print(f"📤 Metrics data exported: {export_path}")
        print("💡 You can now use this CSV file with:")
        print("   • Python pandas/matplotlib for custom analysis")
        print("   • R for statistical analysis")
        print("   • Excel for pivot tables and charts")
        print("   • Any data visualization tool")
        
    except Exception as e:
        print(f"❌ Failed to export data: {e}")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Studio Auto-Labeling Execution Metrics Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s summary                           # Show recent execution summary
  %(prog)s scatter                           # Create scatter plot
  %(prog)s trends                            # Show performance trends
  %(prog)s analysis                          # Generate comprehensive analysis
  %(prog)s regression                        # Show regression analysis
  %(prog)s report --output my_report.txt     # Generate text report
  %(prog)s export --output analysis.csv     # Export data for analysis
        """
    )
    
    # Global options
    parser.add_argument("--metrics-dir", default="execution_metrics",
                       help="Directory containing metrics data (default: execution_metrics)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Show execution summary")
    summary_parser.add_argument("--days", type=int, default=30,
                               help="Number of recent days to include (default: 30)")
    
    # Scatter plot command
    scatter_parser = subparsers.add_parser("scatter", help="Generate scatter plot")
    scatter_parser.add_argument("--show", action="store_true",
                               help="Display plot instead of saving")
    
    # Trends command
    trends_parser = subparsers.add_parser("trends", help="Generate performance trends")
    trends_parser.add_argument("--show", action="store_true",
                              help="Display plot instead of saving")
    
    # Analysis command
    analysis_parser = subparsers.add_parser("analysis", help="Generate comprehensive analysis")
    
    # Regression command  
    regression_parser = subparsers.add_parser("regression", help="Show regression analysis")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate text report")
    report_parser.add_argument("--output", "-o", help="Output file path")
    report_parser.add_argument("--quiet", "-q", action="store_true",
                              help="Don't display insights on console")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export data for analysis")
    export_parser.add_argument("--output", "-o", help="Output CSV file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    setup_logging(args.verbose)
    
    # Route to appropriate command handler
    command_handlers = {
        "summary": cmd_summary,
        "scatter": cmd_scatter,
        "trends": cmd_trends,
        "analysis": cmd_analysis,
        "regression": cmd_regression,
        "report": cmd_report,
        "export": cmd_export
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        parser.print_help()

if __name__ == "__main__":
    main()