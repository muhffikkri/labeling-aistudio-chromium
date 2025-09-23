"""
Demo sederhana untuk menunjukkan fitur request counter yang telah diimplementasi.
"""
import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core_logic.browser_automation import Automation
import logging
import time

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def demo_request_counter():
    """Demo request counter functionality dengan simulasi batch processing"""
    print("🚀 Demo: Request Counter untuk Monitoring Quota API")
    print("=" * 60)
    
    # Create browser automation instance
    browser = Automation(user_data_dir="demo_data", log_folder=Path("demo_logs"))
    
    print("\n1. Simulasi proses batch dengan request counting:")
    
    # Simulasi 3 batch processing
    for batch_num in range(1, 4):
        print(f"\n--- Processing Batch {batch_num} ---")
        
        # Log stats sebelum batch
        stats_before = browser.get_request_stats()
        print(f"📊 Before: {stats_before['total_requests']} requests total, {stats_before['requests_per_minute']:.1f} req/min")
        
        # Simulate API call (ini akan dipanggil oleh get_raw_response_for_batch)
        browser._increment_request_counter()
        
        # Log stats setelah batch
        stats_after = browser.get_request_stats()
        print(f"✅ After: {stats_after['total_requests']} requests total, {stats_after['requests_per_minute']:.1f} req/min")
        
        # Simulasi delay antar batch
        time.sleep(1)
    
    # Final statistics
    print("\n2. Final Statistics:")
    final_stats = browser.get_request_stats()
    print(f"🎯 Total Requests: {final_stats['total_requests']}")
    print(f"⏱️  Session Duration: {final_stats['elapsed_minutes']:.2f} minutes")
    print(f"📈 Current Rate: {final_stats['requests_per_minute']:.1f} requests/minute")
    print(f"📊 Estimated Hourly Rate: {final_stats['estimated_hourly_rate']:.0f} requests/hour")
    
    # Quota monitoring demonstration
    print("\n3. Quota Monitoring Example:")
    quota_limit = 60  # Misalkan quota 60 requests per jam
    current_rate = final_stats['estimated_hourly_rate']
    
    if current_rate > quota_limit:
        print(f"⚠️  WARNING: Current rate ({current_rate:.0f} req/hr) exceeds quota ({quota_limit} req/hr)")
        print("   Consider adding delays between requests or reducing batch size.")
    else:
        print(f"✅ OK: Current rate ({current_rate:.0f} req/hr) is within quota ({quota_limit} req/hr)")
    
    print("\n4. Implementation Details:")
    print("✨ Request counter automatically tracks:")
    print("   • Total API calls made during session")
    print("   • Request rate (requests per minute)")
    print("   • Estimated hourly consumption")
    print("   • Session duration")
    print("\n📝 Logs will show these statistics for each batch, helping you:")
    print("   • Monitor quota usage in real-time")
    print("   • Identify if you're approaching limits")
    print("   • Adjust processing speed if needed")
    
    # Clean up
    browser.close_session()
    print(f"\n🎉 Demo completed! Request counter is ready for production use.")

if __name__ == "__main__":
    demo_request_counter()