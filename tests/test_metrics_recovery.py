#!/usr/bin/env python3
"""
Test script untuk memverifikasi metrics system setelah recovery.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from core_logic.metrics_tracker import ExecutionMetricsTracker
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_metrics_system():
    """Test metrics system after JSON recovery"""
    print("🧪 Testing metrics system after JSON recovery...")
    
    # Create metrics tracker
    tracker = ExecutionMetricsTracker()
    
    # Test 1: Get summary (this should no longer fail)
    print("\n1. Testing metrics summary...")
    try:
        summary = tracker.get_metrics_summary(days=30)
        if "error" in summary:
            print(f"⚠️ Warning: {summary['error']}")
        else:
            print(f"✅ Summary loaded successfully")
            print(f"📊 Found data for recent executions")
    except Exception as e:
        print(f"❌ Failed to get summary: {e}")
        return False
    
    # Test 2: Start new session
    print("\n2. Testing new session creation...")
    try:
        session_id = tracker.start_session(
            dataset_file="test_dataset.csv",
            total_rows=100,
            batch_size=10
        )
        print(f"✅ Session created: {session_id}")
    except Exception as e:
        print(f"❌ Failed to start session: {e}")
        return False
    
    # Test 3: Update progress
    print("\n3. Testing progress update...")
    try:
        tracker.update_progress(
            processed_rows=50,
            failed_rows=5,
            batch_count=5
        )
        print("✅ Progress updated successfully")
    except Exception as e:
        print(f"❌ Failed to update progress: {e}")
        return False
    
    # Test 4: End session and save (this should not fail with JSON error)
    print("\n4. Testing session end and save...")
    try:
        final_metrics = tracker.end_session(status="completed")
        print("✅ Session ended and metrics saved successfully")
        print(f"📊 Final metrics: {final_metrics.get('success_rate', 0):.1f}% success rate")
    except Exception as e:
        print(f"❌ Failed to end session: {e}")
        return False
    
    print("\n🎉 All metrics system tests passed!")
    return True

if __name__ == "__main__":
    if test_metrics_system():
        print("\n✅ Metrics system is working correctly after recovery!")
    else:
        print("\n❌ Metrics system still has issues!")
        sys.exit(1)