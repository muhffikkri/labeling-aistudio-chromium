"""
Test script untuk memverifikasi fungsi request counter pada browser automation.
"""
import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core_logic.browser_automation import Automation
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_request_counter():
    """Test request counter functionality"""
    print("🧪 Testing request counter functionality...")
    
    # Create browser automation instance with dummy parameters
    browser = Automation(user_data_dir="test_data", log_folder=Path("test_logs"))
    
    # Test initial state
    stats = browser.get_request_stats()
    print(f"Initial stats: {stats}")
    assert stats['total_requests'] == 0, "Initial total should be 0"
    
    # Test increment
    browser._increment_request_counter()
    stats = browser.get_request_stats()
    print(f"After increment: {stats}")
    assert stats['total_requests'] == 1, "Total should be 1 after increment"
    
    # Test multiple increments
    for i in range(5):
        browser._increment_request_counter()
    
    stats = browser.get_request_stats()
    print(f"After 5 more increments: {stats}")
    assert stats['total_requests'] == 6, "Total should be 6 after 6 increments"
    
    # Test reset session counter
    browser.request_count = 0  # Simulate reset
    browser._increment_request_counter()
    stats = browser.get_request_stats()
    print(f"After simulated reset: {stats}")
    assert stats['total_requests'] == 1, "Total should be 1 after reset and increment"
    
    # Test request rate calculations
    stats = browser.get_request_stats()
    print(f"Request rate stats: {stats['requests_per_minute']:.2f} req/min, {stats['estimated_hourly_rate']:.2f} req/hr")
    assert stats['requests_per_minute'] >= 0, "Request rate should be non-negative"
    assert stats['estimated_hourly_rate'] >= 0, "Hourly rate should be non-negative"
    
    print("✅ All request counter tests passed!")
    
    # Clean up browser
    browser.close_session()

if __name__ == "__main__":
    test_request_counter()