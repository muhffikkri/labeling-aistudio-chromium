"""
Metrics Visualization Utilities

This module provides visualization tools for execution metrics analysis,
including scatter plots, regression analysis, and performance trend charts.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import logging

class MetricsVisualizer:
    """
    Creates visualizations and analysis from execution metrics data.
    """
    
    def __init__(self, metrics_dir: str = "execution_metrics"):
        """
        Initialize the visualizer.
        
        Args:
            metrics_dir: Directory containing metrics files
        """
        self.metrics_dir = Path(metrics_dir)
        self.json_file = self.metrics_dir / "execution_metrics.json"
        self.csv_file = self.metrics_dir / "execution_metrics.csv"
        self.output_dir = self.metrics_dir / "visualizations"
        self.output_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def load_data(self) -> pd.DataFrame:
        """
        Load metrics data from CSV file.
        
        Returns:
            DataFrame with metrics data
        """
        try:
            if not self.csv_file.exists():
                raise FileNotFoundError(f"Metrics file not found: {self.csv_file}")
            
            df = pd.read_csv(self.csv_file)
            
            # Convert timestamp columns
            if 'start_timestamp' in df.columns:
                df['start_timestamp'] = pd.to_datetime(df['start_timestamp'])
            if 'end_timestamp' in df.columns:
                df['end_timestamp'] = pd.to_datetime(df['end_timestamp'])
            
            # Filter out invalid data
            df = df[(df['duration_seconds'] > 0) & (df['processed_rows'] > 0)]
            
            self.logger.info(f"Loaded {len(df)} execution records")
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to load metrics data: {e}")
            raise
    
    def create_duration_vs_rows_scatter(self, save_plot: bool = True) -> str:
        """
        Create scatter plot of duration vs number of rows with regression line.
        
        Args:
            save_plot: Whether to save the plot to file
            
        Returns:
            Path to saved plot file
        """
        df = self.load_data()
        
        if len(df) < 2:
            raise ValueError("Need at least 2 data points for scatter plot")
        
        # Create figure and axis
        plt.figure(figsize=(12, 8))
        
        # Create scatter plot
        plt.scatter(df['processed_rows'], df['duration_seconds'], 
                   alpha=0.6, s=60, edgecolors='black', linewidth=0.5)
        
        # Add regression line
        x = df['processed_rows'].values
        y = df['duration_seconds'].values
        
        # Calculate linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        line_x = np.linspace(x.min(), x.max(), 100)
        line_y = slope * line_x + intercept
        
        plt.plot(line_x, line_y, 'r-', linewidth=2, 
                label=f'Linear Regression\ny = {slope:.4f}x + {intercept:.2f}\nR² = {r_value**2:.4f}')
        
        # Formatting
        plt.xlabel('Number of Processed Rows', fontsize=12, fontweight='bold')
        plt.ylabel('Duration (seconds)', fontsize=12, fontweight='bold')
        plt.title('Processing Duration vs Number of Rows\nPerformance Analysis', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.legend(loc='upper left')
        plt.grid(True, alpha=0.3)
        
        # Add statistics text box
        stats_text = f"""Statistics:
Correlation: {r_value:.4f}
R²: {r_value**2:.4f}
P-value: {p_value:.2e}
Std Error: {std_err:.4f}
Data Points: {len(df)}"""
        
        plt.text(0.98, 0.02, stats_text, transform=plt.gca().transAxes,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                verticalalignment='bottom', horizontalalignment='right',
                fontsize=9, fontfamily='monospace')
        
        plt.tight_layout()
        
        if save_plot:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_file = self.output_dir / f"duration_vs_rows_scatter_{timestamp}.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved scatter plot: {plot_file}")
            return str(plot_file)
        
        plt.show()
        return ""
    
    def create_performance_trends(self, save_plot: bool = True) -> str:
        """
        Create performance trends over time.
        
        Args:
            save_plot: Whether to save the plot to file
            
        Returns:
            Path to saved plot file
        """
        df = self.load_data()
        
        if len(df) < 2:
            raise ValueError("Need at least 2 data points for trends")
        
        # Sort by timestamp
        df = df.sort_values('start_timestamp')
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Execution Performance Trends Over Time', fontsize=16, fontweight='bold')
        
        # 1. Duration over time
        axes[0, 0].plot(df['start_timestamp'], df['duration_seconds'], 
                       marker='o', linewidth=2, markersize=4)
        axes[0, 0].set_title('Processing Duration Over Time')
        axes[0, 0].set_ylabel('Duration (seconds)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Rows processed over time
        axes[0, 1].plot(df['start_timestamp'], df['processed_rows'], 
                       marker='s', color='green', linewidth=2, markersize=4)
        axes[0, 1].set_title('Rows Processed Over Time')
        axes[0, 1].set_ylabel('Number of Rows')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Success rate over time
        axes[1, 0].plot(df['start_timestamp'], df['success_rate'], 
                       marker='^', color='orange', linewidth=2, markersize=4)
        axes[1, 0].set_title('Success Rate Over Time')
        axes[1, 0].set_ylabel('Success Rate (%)')
        axes[1, 0].set_ylim(0, 100)
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Processing speed over time
        axes[1, 1].plot(df['start_timestamp'], df['rows_per_second'], 
                       marker='d', color='purple', linewidth=2, markersize=4)
        axes[1, 1].set_title('Processing Speed Over Time')
        axes[1, 1].set_ylabel('Rows per Second')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_plot:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_file = self.output_dir / f"performance_trends_{timestamp}.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved trends plot: {plot_file}")
            return str(plot_file)
        
        plt.show()
        return ""
    
    def create_comprehensive_analysis(self, save_plot: bool = True) -> Dict[str, str]:
        """
        Create comprehensive analysis dashboard with multiple visualizations.
        
        Args:
            save_plot: Whether to save plots to files
            
        Returns:
            Dictionary with paths to saved plot files
        """
        df = self.load_data()
        
        if len(df) < 2:
            raise ValueError("Need at least 2 data points for analysis")
        
        plots = {}
        
        # 1. Main scatter plot with regression
        plots['scatter'] = self.create_duration_vs_rows_scatter(save_plot)
        
        # 2. Performance trends
        plots['trends'] = self.create_performance_trends(save_plot)
        
        # 3. Distribution analysis
        plots['distributions'] = self._create_distributions_plot(df, save_plot)
        
        # 4. Correlation matrix
        plots['correlations'] = self._create_correlation_matrix(df, save_plot)
        
        return plots
    
    def _create_distributions_plot(self, df: pd.DataFrame, save_plot: bool) -> str:
        """Create distribution plots for key metrics."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Metrics Distributions', fontsize=16, fontweight='bold')
        
        # Duration distribution
        axes[0, 0].hist(df['duration_seconds'], bins=20, alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Duration Distribution')
        axes[0, 0].set_xlabel('Duration (seconds)')
        axes[0, 0].set_ylabel('Frequency')
        
        # Rows processed distribution
        axes[0, 1].hist(df['processed_rows'], bins=20, alpha=0.7, color='green', edgecolor='black')
        axes[0, 1].set_title('Rows Processed Distribution')
        axes[0, 1].set_xlabel('Number of Rows')
        axes[0, 1].set_ylabel('Frequency')
        
        # Success rate distribution
        axes[1, 0].hist(df['success_rate'], bins=20, alpha=0.7, color='orange', edgecolor='black')
        axes[1, 0].set_title('Success Rate Distribution')
        axes[1, 0].set_xlabel('Success Rate (%)')
        axes[1, 0].set_ylabel('Frequency')
        
        # Processing speed distribution
        axes[1, 1].hist(df['rows_per_second'], bins=20, alpha=0.7, color='purple', edgecolor='black')
        axes[1, 1].set_title('Processing Speed Distribution')
        axes[1, 1].set_xlabel('Rows per Second')
        axes[1, 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        
        if save_plot:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_file = self.output_dir / f"distributions_{timestamp}.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            return str(plot_file)
        
        plt.show()
        return ""
    
    def _create_correlation_matrix(self, df: pd.DataFrame, save_plot: bool) -> str:
        """Create correlation matrix heatmap."""
        # Select numeric columns for correlation
        numeric_cols = ['duration_seconds', 'processed_rows', 'batch_count', 
                       'success_rate', 'rows_per_second', 'batch_size']
        
        # Filter to existing columns
        available_cols = [col for col in numeric_cols if col in df.columns]
        correlation_df = df[available_cols]
        
        # Calculate correlation matrix
        corr_matrix = correlation_df.corr()
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, fmt='.3f', cbar_kws={'label': 'Correlation Coefficient'})
        plt.title('Metrics Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if save_plot:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_file = self.output_dir / f"correlations_{timestamp}.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            return str(plot_file)
        
        plt.show()
        return ""
    
    def get_regression_analysis(self) -> Dict:
        """
        Get detailed regression analysis for duration vs rows.
        
        Returns:
            Dictionary with regression statistics and predictions
        """
        df = self.load_data()
        
        if len(df) < 2:
            raise ValueError("Need at least 2 data points for regression")
        
        x = df['processed_rows'].values.reshape(-1, 1)
        y = df['duration_seconds'].values
        
        # Linear regression
        model = LinearRegression()
        model.fit(x, y)
        y_pred = model.predict(x)
        
        # Statistics
        r2 = r2_score(y, y_pred)
        slope = model.coef_[0]
        intercept = model.intercept_
        
        # Additional statistics
        correlation = np.corrcoef(x.flatten(), y)[0, 1]
        
        analysis = {
            "model": {
                "slope": float(slope),
                "intercept": float(intercept),
                "equation": f"duration = {slope:.6f} * rows + {intercept:.2f}"
            },
            "statistics": {
                "r_squared": float(r2),
                "correlation": float(correlation),
                "data_points": len(df),
                "mean_duration": float(df['duration_seconds'].mean()),
                "mean_rows": float(df['processed_rows'].mean())
            },
            "predictions": {
                "100_rows": float(model.predict([[100]])[0]),
                "500_rows": float(model.predict([[500]])[0]),
                "1000_rows": float(model.predict([[1000]])[0]),
                "5000_rows": float(model.predict([[5000]])[0])
            }
        }
        
        return analysis
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate a comprehensive analysis report.
        
        Args:
            output_file: Optional path for output file
            
        Returns:
            Path to generated report file
        """
        df = self.load_data()
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"metrics_analysis_report_{timestamp}.txt"
        
        # Get regression analysis
        regression = self.get_regression_analysis()
        
        # Generate report content
        report = f"""
EXECUTION METRICS ANALYSIS REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
================================================

DATA SUMMARY:
- Total executions: {len(df)}
- Date range: {df['start_timestamp'].min()} to {df['start_timestamp'].max()}

PERFORMANCE STATISTICS:
- Average duration: {df['duration_seconds'].mean():.2f} seconds
- Median duration: {df['duration_seconds'].median():.2f} seconds
- Average rows processed: {df['processed_rows'].mean():.0f}
- Median rows processed: {df['processed_rows'].median():.0f}
- Average success rate: {df['success_rate'].mean():.2f}%
- Average processing speed: {df['rows_per_second'].mean():.2f} rows/second

REGRESSION ANALYSIS (Duration vs Rows):
- Equation: {regression['model']['equation']}
- R²: {regression['statistics']['r_squared']:.4f}
- Correlation: {regression['statistics']['correlation']:.4f}

PERFORMANCE PREDICTIONS:
- 100 rows: {regression['predictions']['100_rows']:.2f} seconds
- 500 rows: {regression['predictions']['500_rows']:.2f} seconds
- 1000 rows: {regression['predictions']['1000_rows']:.2f} seconds
- 5000 rows: {regression['predictions']['5000_rows']:.2f} seconds

TRENDS:
- Duration trend: {"Improving" if df['duration_seconds'].iloc[-1] < df['duration_seconds'].iloc[0] else "Stable/Declining"}
- Success rate trend: {"Improving" if df['success_rate'].iloc[-1] > df['success_rate'].iloc[0] else "Stable/Declining"}
- Processing speed trend: {"Improving" if df['rows_per_second'].iloc[-1] > df['rows_per_second'].iloc[0] else "Stable/Declining"}
"""
        
        with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
            f.write(report)
        
        self.logger.info(f"Generated analysis report: {output_file}")
        return str(output_file)