#!/usr/bin/env python3
"""
Test script untuk memvalidasi perbaikan screenshot error handling.
"""

import logging
import tempfile
import time
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def test_safe_screenshot():
    """Test implementasi safe screenshot."""
    logging.info("🧪 Starting safe screenshot test...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Import setelah setup logging
        import sys
        sys.path.insert(0, str(Path("../src").absolute()))
        
        from core_logic.browser_automation import Automation
        
        # Test 1: Create Automation instance dengan mock log folder
        log_folder = temp_path / "logs"
        log_folder.mkdir(exist_ok=True)
        
        automation = Automation(
            user_data_dir=str(temp_path / "browser_data"),
            log_folder=log_folder
        )
        
        # Test 2: Test _safe_screenshot method tanpa browser aktif
        logging.info("📋 Testing safe screenshot without active browser...")
        
        # Seharusnya tidak crash meskipun page tidak ada
        automation._safe_screenshot("test_screenshot.png", "Test without browser")
        
        logging.info("✅ Safe screenshot test passed - no crash when page is None!")
        
        # Test 3: Test dengan mock page yang sudah closed
        logging.info("📋 Testing safe screenshot with closed page...")
        
        # Simulate closed page
        automation.page = None
        automation._safe_screenshot("test_screenshot_2.png", "Test with None page")
        
        logging.info("✅ Safe screenshot test passed - handled None page gracefully!")
        
        logging.info("🎉 ALL SAFE SCREENSHOT TESTS PASSED!")

if __name__ == "__main__":
    test_safe_screenshot()