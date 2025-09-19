# 📊 Execution Metrics Analysis Guide

This guide provides detailed information about the execution metrics tracking and analysis system built into the AI Studio Auto-Labeling Tool.

## 🎯 Overview

The metrics system automatically captures, stores, and analyzes execution data to provide insights into:

- **Performance Patterns**: How processing time relates to data size
- **Efficiency Trends**: Performance changes over time
- **Capacity Planning**: Predictions for processing large datasets
- **Bottleneck Identification**: Areas for optimization

## 📈 Automatic Tracking

### What Gets Tracked

Every execution automatically captures:

```json
{
  "session_id": "20250103_141530_abc123",
  "timestamp": "2025-01-03T14:15:30.123456",
  "duration_seconds": 245.67,
  "total_rows": 150,
  "processed_rows": 147,
  "failed_rows": 3,
  "success_rate": 98.0,
  "batch_size": 25,
  "input_file": "datasets/customer_reviews.xlsx",
  "prompt_file": "prompts/sentiment.txt"
}
```

### Storage Format

- **JSON Files**: `execution_metrics/sessions/YYYY-MM-DD/session_id.json`
- **CSV Export**: Consolidated data for external analysis
- **Automatic Cleanup**: Configurable retention periods

## 🛠️ Analysis CLI Tool

The `analyze_metrics.py` script provides comprehensive analysis capabilities:

### Basic Commands

```bash
# Show recent execution summary (last 30 days)
python analyze_metrics.py summary

# Show summary for specific period
python analyze_metrics.py summary --days 7

# Generate scatter plot: duration vs rows
python analyze_metrics.py scatter

# Show performance trends over time
python analyze_metrics.py trends

# Generate comprehensive analysis dashboard
python analyze_metrics.py analysis
```

### Advanced Analysis

```bash
# Detailed regression analysis with statistics
python analyze_metrics.py regression

# Generate comprehensive text report
python analyze_metrics.py report --output performance_report.txt

# Export raw data for external analysis
python analyze_metrics.py export --output analysis_data.csv

# Use custom metrics directory
python analyze_metrics.py summary --metrics-dir custom_metrics_folder
```

## 📊 Understanding the Analysis

### Summary Report

The summary provides key performance indicators:

```
📊 EXECUTION METRICS SUMMARY
==================================================
📅 Period: Last 30 days
🧪 Total executions: 15
⏱️  Average duration: 187.45 seconds
📈 Duration range: 45.20s - 425.80s
📋 Average rows processed: 1,247
📊 Rows range: 100 - 3,500
✅ Average success rate: 96.8%
🎯 Total rows processed: 18,705
```

### Regression Analysis

The regression analysis provides predictive insights:

```
🔍 REGRESSION ANALYSIS
==================================================
📐 Linear Equation:
   Duration = 0.0847 × Rows + 23.45

📊 Statistics:
   R² (coefficient of determination): 0.8234
   Correlation coefficient: 0.9074
   Data points: 15
   Mean duration: 187.45 seconds
   Mean rows: 1,247

🔮 Duration Predictions:
   100 Rows: 31.92 seconds
   500 Rows: 65.80 seconds
   1000 Rows: 108.15 seconds
   2000 Rows: 192.85 seconds
   5000 Rows: 446.95 seconds

💡 Interpretation:
   🟢 Strong linear relationship - Duration scales predictably with row count
```

### Interpretation Guide

**R² (R-squared) Values:**

- **> 0.8**: Strong linear relationship - very predictable scaling
- **0.5 - 0.8**: Moderate relationship - generally predictable with some variance
- **< 0.5**: Weak relationship - other factors significantly affect performance

**Color Coding:**

- 🟢 **Green**: Strong correlation, reliable predictions
- 🟡 **Yellow**: Moderate correlation, reasonable estimates
- 🔴 **Red**: Weak correlation, predictions less reliable

## 📈 Visualization Features

### Scatter Plot Analysis

Shows the relationship between data size and processing time:

- **Data Points**: Each execution as a point (rows vs duration)
- **Trend Line**: Linear regression line showing the general pattern
- **R² Value**: Correlation strength displayed on chart
- **Outliers**: Unusual executions that deviate from the pattern

### Performance Trends

Tracks performance changes over time:

- **Duration Trends**: How processing speed changes over time
- **Success Rate Trends**: Quality metrics over time
- **Volume Trends**: Data size patterns over time
- **Moving Averages**: Smoothed trends to identify patterns

### Comprehensive Dashboard

Combines multiple visualizations:

- **Scatter Plot**: Size vs duration relationship
- **Trend Lines**: Performance over time
- **Success Rate Analysis**: Quality metrics
- **Distribution Histograms**: Data size and duration distributions

## 🔧 Customization Options

### Command Line Options

```bash
# Display plots instead of saving them
python analyze_metrics.py scatter --show
python analyze_metrics.py trends --show

# Specify custom output files
python analyze_metrics.py report --output "reports/weekly_performance.txt"
python analyze_metrics.py export --output "data/metrics_$(date +%Y%m%d).csv"

# Verbose logging for debugging
python analyze_metrics.py analysis --verbose

# Custom metrics directory
python analyze_metrics.py summary --metrics-dir "archived_metrics"
```

### Configuration

Modify behavior by editing the metrics tracker configuration:

```python
# In src/core_logic/metrics_tracker.py
class ExecutionMetricsTracker:
    def __init__(self, base_dir="execution_metrics"):
        self.base_dir = Path(base_dir)
        self.retention_days = 90  # Keep metrics for 90 days
        self.auto_cleanup = True  # Automatic old data cleanup
```

## 🎯 Use Cases

### Performance Optimization

1. **Identify Bottlenecks**: Find executions that take longer than expected
2. **Optimize Batch Sizes**: Determine optimal batch size for your data
3. **Resource Planning**: Predict resource needs for large datasets

### Capacity Planning

```bash
# Analyze current performance
python analyze_metrics.py regression

# Use predictions for planning:
# "For 10,000 rows, expect ~15 minutes processing time"
# "Success rate typically 96%+, plan for ~4% retry overhead"
```

### Quality Monitoring

```bash
# Track success rates over time
python analyze_metrics.py trends

# Look for degrading performance patterns
# Monitor error rates and processing efficiency
```

### Data Export for Advanced Analysis

```bash
# Export for statistical analysis in R
python analyze_metrics.py export --output data_for_r.csv

# Export for custom Python analysis
python analyze_metrics.py export --output data.csv
# Then: pandas.read_csv('data.csv') in your scripts

# Export for Excel analysis
python analyze_metrics.py export --output metrics.csv
# Open in Excel for pivot tables and custom charts
```

## 🔍 Troubleshooting

### No Data Available

```bash
# Check if metrics directory exists
ls -la execution_metrics/

# Verify recent executions have run
python src/main.py --input-file "datasets/sample.xlsx" --debug
```

### Incomplete Analysis

```bash
# Check for minimum data requirements
python analyze_metrics.py summary --verbose

# Minimum 3-5 executions needed for meaningful regression analysis
```

### Visualization Issues

```bash
# Install required packages
pip install matplotlib seaborn scikit-learn pandas

# Test with show mode first
python analyze_metrics.py scatter --show
```

## 📚 Integration Examples

### Automated Reporting

Create a scheduled script for regular performance reports:

```bash
#!/bin/bash
# weekly_performance_report.sh

DATE=$(date +%Y-%m-%d)
REPORT_DIR="reports/weekly"
mkdir -p $REPORT_DIR

# Generate comprehensive report
python analyze_metrics.py report --output "$REPORT_DIR/performance_$DATE.txt"

# Export data for archiving
python analyze_metrics.py export --output "$REPORT_DIR/data_$DATE.csv"

# Generate visualizations
python analyze_metrics.py analysis

echo "Weekly performance report generated: $REPORT_DIR/performance_$DATE.txt"
```

### Custom Analysis Scripts

```python
# custom_analysis.py
import pandas as pd
from pathlib import Path

# Load exported metrics data
data = pd.read_csv('metrics_export.csv')

# Custom analysis
efficiency = data['processed_rows'] / data['duration_seconds']
print(f"Average processing efficiency: {efficiency.mean():.2f} rows/second")

# Identify best performing sessions
top_sessions = data.nlargest(5, efficiency)
print("Top 5 most efficient sessions:")
print(top_sessions[['session_id', 'processed_rows', 'duration_seconds']])
```

## 🎨 Best Practices

### Regular Monitoring

- **Weekly Reviews**: Check performance trends weekly
- **Before Major Changes**: Baseline performance before system changes
- **After Optimization**: Verify improvements with before/after analysis

### Data Hygiene

- **Regular Cleanup**: Archive old metrics data periodically
- **Backup Important Data**: Save key performance reports
- **Version Control**: Track metrics alongside code changes

### Performance Baselines

```bash
# Establish baseline performance
python analyze_metrics.py regression > baseline_performance.txt

# After optimization, compare:
python analyze_metrics.py regression > optimized_performance.txt
diff baseline_performance.txt optimized_performance.txt
```

## 🚀 Advanced Features

### Programmatic Access

```python
# Direct access to metrics in your Python scripts
from src.core_logic.metrics_tracker import ExecutionMetricsTracker
from src.core_logic.metrics_visualizer import MetricsVisualizer

# Load metrics data
tracker = ExecutionMetricsTracker()
summary = tracker.get_metrics_summary(days=30)

# Generate custom visualizations
visualizer = MetricsVisualizer()
regression_data = visualizer.get_regression_analysis()

print(f"R² = {regression_data['statistics']['r_squared']:.4f}")
```

### Custom Metrics

Extend the system to track additional metrics:

```python
# In your processing code
metrics_tracker.add_custom_metric('memory_usage_mb', memory_mb)
metrics_tracker.add_custom_metric('cpu_percent', cpu_usage)
metrics_tracker.add_custom_metric('error_types', error_breakdown)
```

## 📞 Support

For questions about the metrics system:

1. **Check Logs**: Look for metrics-related errors in execution logs
2. **Verify Installation**: Ensure matplotlib, seaborn, sklearn are installed
3. **Test Basic Commands**: Start with `python analyze_metrics.py summary`
4. **Review Data**: Check `execution_metrics/` directory structure

---

**📊 Ready to optimize your processing performance? Start with `python analyze_metrics.py summary` to see your current metrics!**
