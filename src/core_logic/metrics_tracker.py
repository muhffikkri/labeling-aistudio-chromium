"""
Execution Metrics Tracker

This module handles tracking, storing, and analyzing execution metrics
for the AI Studio Auto-Labeling system. It records timestamp, duration,
row counts, and other performance data for analysis and visualization.
"""

import json
import csv
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

class ExecutionMetricsTracker:
    """
    Tracks and stores execution metrics for performance analysis.
    
    Metrics tracked:
    - timestamp: When the execution started
    - duration: How long the execution took (seconds)
    - total_rows: Total number of rows in dataset
    - processed_rows: Number of successfully processed rows
    - failed_rows: Number of failed rows
    - batch_count: Number of batches processed
    - batch_size: Average batch size used
    - success_rate: Percentage of successful processing
    - session_id: Unique identifier for this execution
    """
    
    def __init__(self, metrics_dir: str = "execution_metrics"):
        """
        Initialize the metrics tracker.
        
        Args:
            metrics_dir: Directory to store metrics files
        """
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(exist_ok=True)
        
        # Current session data
        self.session_id = None
        self.start_time = None
        self.session_data = {}
        
        # File paths
        self.json_file = self.metrics_dir / "execution_metrics.json"
        self.csv_file = self.metrics_dir / "execution_metrics.csv"
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def start_session(self, dataset_file: str, total_rows: int, batch_size: int) -> str:
        """
        Start a new execution session.
        
        Args:
            dataset_file: Path to the dataset file
            total_rows: Total number of rows in the dataset
            batch_size: Batch size being used
            
        Returns:
            session_id: Unique identifier for this session
        """
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = time.time()
        
        self.session_data = {
            "session_id": self.session_id,
            "dataset_file": str(dataset_file),
            "start_timestamp": datetime.now().isoformat(),
            "total_rows": total_rows,
            "batch_size": batch_size,
            "processed_rows": 0,
            "failed_rows": 0,
            "batch_count": 0,
            "duration_seconds": 0,
            "success_rate": 0.0,
            "status": "running"
        }
        
        self.logger.info(f"Started metrics tracking session: {self.session_id}")
        return self.session_id
    
    def update_progress(self, processed_rows: int, failed_rows: int, batch_count: int):
        """
        Update session progress metrics.
        
        Args:
            processed_rows: Number of rows successfully processed so far
            failed_rows: Number of rows that failed processing
            batch_count: Number of batches completed
        """
        if not self.session_id:
            self.logger.warning("No active session to update")
            return
            
        self.session_data.update({
            "processed_rows": processed_rows,
            "failed_rows": failed_rows,
            "batch_count": batch_count,
            "success_rate": (processed_rows / max(1, processed_rows + failed_rows)) * 100
        })
    
    def end_session(self, status: str = "completed") -> Dict:
        """
        End the current session and save metrics.
        
        Args:
            status: Final status of the execution ('completed', 'failed', 'interrupted')
            
        Returns:
            Complete session metrics dictionary
        """
        if not self.session_id or not self.start_time:
            self.logger.warning("No active session to end")
            return {}
            
        # Calculate final metrics
        end_time = time.time()
        duration = end_time - self.start_time
        
        self.session_data.update({
            "end_timestamp": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2),
            "duration_minutes": round(duration / 60, 2),
            "status": status,
            "rows_per_second": round(self.session_data["processed_rows"] / max(1, duration), 2),
            "avg_batch_processing_time": round(duration / max(1, self.session_data["batch_count"]), 2)
        })
        
        # Save to files
        self._save_to_json()
        self._save_to_csv()
        
        self.logger.info(f"Completed metrics tracking session: {self.session_id}")
        self.logger.info(f"Duration: {duration:.2f}s, Processed: {self.session_data['processed_rows']} rows")
        
        # Reset session
        session_data = self.session_data.copy()
        self.session_id = None
        self.start_time = None
        self.session_data = {}
        
        return session_data
    
    def _save_to_json(self):
        """Save metrics to JSON file for detailed analysis."""
        try:
            # Load existing data
            if self.json_file.exists():
                with open(self.json_file, 'r', encoding='utf-8', errors='replace') as f:
                    data = json.load(f)
            else:
                data = {"executions": []}
            
            # Add current session
            data["executions"].append(self.session_data)
            
            # Save back to file
            with open(self.json_file, 'w', encoding='utf-8', errors='replace') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save JSON metrics: {e}")
    
    def _save_to_csv(self):
        """Save metrics to CSV file for easy analysis and plotting."""
        try:
            # Define CSV columns
            columns = [
                "session_id", "start_timestamp", "end_timestamp", 
                "duration_seconds", "duration_minutes", "total_rows", 
                "processed_rows", "failed_rows", "batch_count", "batch_size",
                "success_rate", "rows_per_second", "avg_batch_processing_time",
                "status", "dataset_file"
            ]
            
            # Check if file exists to determine if we need headers
            file_exists = self.csv_file.exists()
            
            # Write to CSV
            with open(self.csv_file, 'a', newline='', encoding='utf-8', errors='replace') as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                
                if not file_exists:
                    writer.writeheader()
                
                # Write only the columns that exist in session_data
                row_data = {col: self.session_data.get(col, '') for col in columns}
                writer.writerow(row_data)
                
        except Exception as e:
            self.logger.error(f"Failed to save CSV metrics: {e}")
    
    def get_metrics_summary(self, days: int = 30) -> Dict:
        """
        Get summary statistics for recent executions.
        
        Args:
            days: Number of recent days to include in summary
            
        Returns:
            Dictionary with summary statistics
        """
        try:
            if not self.json_file.exists():
                return {"error": "No metrics data available"}
            
            with open(self.json_file, 'r', encoding='utf-8', errors='replace') as f:
                data = json.load(f)
            
            executions = data.get("executions", [])
            if not executions:
                return {"error": "No execution data found"}
            
            # Filter recent executions
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_executions = [
                ex for ex in executions 
                if datetime.fromisoformat(ex.get("start_timestamp", "")) > cutoff_date
            ]
            
            if not recent_executions:
                return {"error": f"No executions found in the last {days} days"}
            
            # Calculate summary statistics
            durations = [ex.get("duration_seconds", 0) for ex in recent_executions]
            row_counts = [ex.get("processed_rows", 0) for ex in recent_executions]
            success_rates = [ex.get("success_rate", 0) for ex in recent_executions]
            
            summary = {
                "period_days": days,
                "total_executions": len(recent_executions),
                "avg_duration_seconds": round(sum(durations) / len(durations), 2),
                "min_duration_seconds": min(durations),
                "max_duration_seconds": max(durations),
                "avg_rows_processed": round(sum(row_counts) / len(row_counts), 2),
                "min_rows_processed": min(row_counts),
                "max_rows_processed": max(row_counts),
                "avg_success_rate": round(sum(success_rates) / len(success_rates), 2),
                "total_rows_processed": sum(row_counts)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics summary: {e}")
            return {"error": str(e)}
    
    def export_for_analysis(self, output_file: Optional[str] = None) -> str:
        """
        Export metrics data in a format suitable for analysis/plotting.
        
        Args:
            output_file: Optional custom output file path
            
        Returns:
            Path to the exported file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.metrics_dir / f"metrics_for_analysis_{timestamp}.csv"
        
        try:
            if not self.json_file.exists():
                raise FileNotFoundError("No metrics data available")
            
            with open(self.json_file, 'r', encoding='utf-8', errors='replace') as f:
                data = json.load(f)
            
            executions = data.get("executions", [])
            
            # Export with columns optimized for analysis
            analysis_columns = [
                "session_id", "start_timestamp", "duration_seconds", 
                "total_rows", "processed_rows", "success_rate",
                "batch_count", "batch_size", "rows_per_second"
            ]
            
            with open(output_file, 'w', newline='', encoding='utf-8', errors='replace') as f:
                writer = csv.DictWriter(f, fieldnames=analysis_columns)
                writer.writeheader()
                
                for execution in executions:
                    row_data = {col: execution.get(col, '') for col in analysis_columns}
                    writer.writerow(row_data)
            
            return str(output_file)
            
        except Exception as e:
            self.logger.error(f"Failed to export metrics for analysis: {e}")
            raise