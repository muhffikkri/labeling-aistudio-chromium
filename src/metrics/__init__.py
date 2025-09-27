"""
Metrics Package

This package provides comprehensive metrics tracking, analysis, and visualization
for the AI Studio Auto-Labeling system.

Components:
- ExecutionMetricsTracker: Core metrics collection and storage
- MetricsVisualizer: Data visualization and analysis tools
- Analysis Scripts: Command-line tools for metrics analysis

Usage:
    from src.metrics.metrics_tracker import ExecutionMetricsTracker
    from src.metrics.metrics_visualizer import MetricsVisualizer
"""

from .metrics_tracker import ExecutionMetricsTracker
from .metrics_visualizer import MetricsVisualizer

__all__ = ['ExecutionMetricsTracker', 'MetricsVisualizer']
__version__ = '1.0.0'