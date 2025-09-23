#!/usr/bin/env python3
"""
JSON Metrics Recovery Tool

This script fixes corrupted execution_metrics.json files by:
1. Detecting and backing up corrupted files
2. Creating a fresh JSON structure
3. Preserving any valid data from CSV if available
"""

import json
import csv
import logging
from pathlib import Path
from datetime import datetime
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def recover_metrics_json():
    """Main recovery function"""
    logger.info("🔧 Starting JSON metrics recovery...")
    
    # Define file paths
    metrics_dir = Path("execution_metrics")
    json_file = metrics_dir / "execution_metrics.json"
    csv_file = metrics_dir / "execution_metrics.csv"
    
    if not metrics_dir.exists():
        logger.error("❌ Execution metrics directory not found")
        return False
    
    # Check if JSON file exists and is corrupted
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info("✅ JSON file is valid, no recovery needed")
            return True
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ JSON file corrupted: {e}")
            logger.info("Creating backup...")
            
            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = json_file.with_suffix(f'.json.corrupted_{timestamp}')
            backup_file.write_bytes(json_file.read_bytes())
            logger.info(f"📁 Backup created: {backup_file}")
    
    # Create fresh JSON structure
    logger.info("🔄 Creating fresh JSON structure...")
    fresh_data = {
        "executions": [],
        "recovery_info": {
            "recovered_at": datetime.now().isoformat(),
            "recovery_reason": "Corrupted JSON file detected and recovered"
        }
    }
    
    # Try to recover data from CSV if available
    if csv_file.exists():
        logger.info("📊 Attempting to recover data from CSV...")
        try:
            recovered_count = 0
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert CSV row back to JSON format
                    execution = {
                        "session_id": row.get("session_id", ""),
                        "dataset_file": row.get("dataset_file", ""),
                        "start_timestamp": row.get("start_timestamp", ""),
                        "end_timestamp": row.get("end_timestamp", ""),
                        "total_rows": int(row.get("total_rows", 0)) if row.get("total_rows", "").isdigit() else 0,
                        "processed_rows": int(row.get("processed_rows", 0)) if row.get("processed_rows", "").isdigit() else 0,
                        "failed_rows": int(row.get("failed_rows", 0)) if row.get("failed_rows", "").isdigit() else 0,
                        "batch_count": int(row.get("batch_count", 0)) if row.get("batch_count", "").isdigit() else 0,
                        "batch_size": int(row.get("batch_size", 0)) if row.get("batch_size", "").isdigit() else 0,
                        "duration_seconds": float(row.get("duration_seconds", 0)) if row.get("duration_seconds", "").replace('.','').isdigit() else 0,
                        "success_rate": float(row.get("success_rate", 0)) if row.get("success_rate", "").replace('.','').isdigit() else 0,
                        "status": row.get("status", "unknown")
                    }
                    fresh_data["executions"].append(execution)
                    recovered_count += 1
            
            logger.info(f"✅ Recovered {recovered_count} execution records from CSV")
        except Exception as e:
            logger.warning(f"⚠️ Could not recover from CSV: {e}")
    
    # Write fresh JSON file
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(fresh_data, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Fresh JSON file created with {len(fresh_data['executions'])} records")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to write fresh JSON file: {e}")
        return False

if __name__ == "__main__":
    if recover_metrics_json():
        logger.info("🎉 Recovery completed successfully!")
    else:
        logger.error("❌ Recovery failed!")
        sys.exit(1)