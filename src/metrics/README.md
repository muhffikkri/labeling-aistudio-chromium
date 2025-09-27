# 📊 Metrics Package

Comprehensive execution metrics tracking, analysis, and visualization for the AI Studio Auto-Labeling system.

## 🚀 Quick Start

```bash
# From project root
python metrics_cli.py summary
python metrics_cli.py all
```

## 📦 Package Components

### Core Modules

- **`metrics_tracker.py`**: Data collection and storage
- **`metrics_visualizer.py`**: Analysis and visualization tools
- **`analyze_metrics.py`**: CLI analysis interface
- **`fix_and_validate_metrics.py`**: Recovery and validation utilities

### CLI Access

- **`../../metrics_cli.py`**: Main entry point from project root
- **`python analyze_metrics.py`**: Direct access from this folder

## 📊 Features

- ✅ **Automatic Data Collection**: Integrated with main labeling process
- ✅ **Multiple Visualizations**: Scatter plots, trends, regression analysis
- ✅ **Data Export**: CSV export for external analysis
- ✅ **Corruption Recovery**: Automatic backup and recovery systems
- ✅ **Performance Analysis**: Success rates, throughput, efficiency metrics

## 📁 Data Storage

```
execution_metrics/
├── execution_metrics.csv    # Primary data store
├── execution_metrics.json   # Detailed session data
├── visualizations/          # Generated plots
└── exports/                 # Analysis exports
```

## 🎯 Usage Examples

### Python Integration

```python
from metrics.metrics_tracker import ExecutionMetricsTracker
from metrics.metrics_visualizer import MetricsVisualizer

# Start tracking
tracker = ExecutionMetricsTracker()
session_id = tracker.start_session("dataset.csv", 1000, 50)

# Update progress
tracker.update_progress(processed=500, failed=10, batches=10)

# End session
final_metrics = tracker.end_session("completed")

# Generate analysis
visualizer = MetricsVisualizer()
visualizer.create_duration_vs_rows_scatter()
```

### Command Line Analysis

```bash
# Summary statistics
python analyze_metrics.py summary --days 7

# Generate visualizations
python analyze_metrics.py visualize

# Export for external analysis
python analyze_metrics.py export --output monthly_data.csv
```

## 🔧 System Integration

The metrics system is automatically integrated with the main labeling process:

1. **Auto-Start**: Session begins when `main.py` starts processing
2. **Real-time Updates**: Progress tracked per batch
3. **Auto-Save**: Data saved on completion, interruption, or failure
4. **Recovery**: Corrupted data automatically recovered from backups

## 📈 Analysis Capabilities

- **Performance Trends**: Track improvements over time
- **Regression Analysis**: Predict processing time for dataset sizes
- **Success Rate Analysis**: Quality metrics and failure patterns
- **Capacity Planning**: Resource estimation for large datasets
- **Optimization Insights**: Batch size and parameter tuning recommendations

## 📖 Documentation

See **`METRICS_GUIDE.md`** for complete documentation including:

- Detailed usage instructions
- Advanced analysis examples
- Troubleshooting guide
- Best practices and optimization tips

---

**Ready to start?** Run `python ../../metrics_cli.py summary` from project root!
