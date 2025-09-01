"""
Script to test the dynamic waiting logic for Gemini AI responses.
This is a simplified version without actually running the browser.
"""
import time

class MockPage:
    """Mock Page class to simulate Playwright Page object"""
    def __init__(self, simulation_mode="normal"):
        self.simulation_mode = simulation_mode
        self.stop_button_visible = True
        self.response_text = ""
        self.start_time = time.time()
        
    def locator(self, selector):
        """Mock locator method"""
        return MockLocator(self)
    
    def query_selector_all(self, selector):
        """Mock query_selector_all method"""
        if "response" in selector:
            if time.time() - self.start_time > 5:
                # After 5 seconds, return mock response containers
                return [MockElement(self)]
            return []
        return []
    
    def evaluate(self, js_code):
        """Mock evaluate method"""
        elapsed = time.time() - self.start_time
        
        # Simulate button disappearing after 8 seconds
        stop_button_gone = elapsed > 8
        
        # Simulate response appearing after 5 seconds
        has_response = elapsed > 5
        
        # Simulate thinking indicator disappearing after 10 seconds
        not_thinking = elapsed > 10
        
        return {
            "stopButtonGone": stop_button_gone,
            "hasStableResponse": has_response,
            "notThinking": not_thinking,
            "probablyDone": (stop_button_gone and has_response) or 
                            (stop_button_gone and not_thinking) or
                            (has_response and not_thinking)
        }
        
    def screenshot(self, path):
        """Mock screenshot method"""
        print(f"Taking screenshot: {path}")


class MockLocator:
    """Mock Locator class"""
    def __init__(self, page):
        self.page = page
        self.first = MockElement(page)
    
    def count(self):
        """Return count of elements"""
        elapsed = time.time() - self.page.start_time
        # Simulate stop button disappearing after 8 seconds
        return 0 if elapsed > 8 else 1


class MockElement:
    """Mock Element class"""
    def __init__(self, page):
        self.page = page
        
    def inner_text(self):
        """Return simulated response text"""
        elapsed = time.time() - self.page.start_time
        
        # Simulate text growing over time
        if elapsed < 5:
            return ""
        elif elapsed < 7:
            return "The answer is"
        elif elapsed < 9:
            return "The answer is based on"
        else:
            return "The answer is based on the information provided."


def test_dynamic_waiting():
    """Test the dynamic waiting logic"""
    page = MockPage()
    
    print("====== TESTING DYNAMIC WAITING LOGIC ======")
    
    # Helper method to detect if generation is complete via JavaScript
    def is_generation_complete_via_js():
        try:
            # Call the mock evaluate method
            return page.evaluate("")
        except Exception as e:
            print(f"! Error checking generation status via JS: {e}")
            return {"probablyDone": False}

    # Track generation status
    generation_started = True  # Assume generation has started
    generation_completed = False
    
    # Dynamic waiting strategy
    max_wait_time = 60  # Maximum seconds to wait (1 minute for testing)
    start_wait_time = time.time()
    wait_interval = 1  # Check every 1 second for faster testing
    progress_shown = False
    stable_content_counter = 0  # Count how many times content remains stable
    
    print("Waiting for model to complete generation...")
    
    # First, make sure we can detect when Stop button disappears
    stop_button_visible = True
    
    # Loop until generation completes or timeout
    while True:
        # Check if we've waited too long
        elapsed = time.time() - start_wait_time
        if elapsed > max_wait_time:
            print(f"! Maximum wait time of {max_wait_time} seconds exceeded.")
            break
            
        # Show waiting progress periodically
        if int(elapsed) % 5 == 0 and not progress_shown:  # Every 5 seconds
            print(f"Still waiting for generation to complete... ({int(elapsed)} seconds)")
            progress_shown = True
        elif int(elapsed) % 5 != 0:
            progress_shown = False
            
        # Strategy 1: If Stop button was visible, wait for it to disappear
        if stop_button_visible:
            try:
                # Check if Stop button is still visible
                new_count = page.locator("button:has-text('Stop')").count()
                if new_count == 0:
                    print(f"✓ Stop button disappeared after {elapsed:.1f} seconds - generation completed")
                    generation_completed = True
                    break
            except Exception:
                # Ignore errors checking button
                pass
        
        # Strategy 2: Use our JavaScript helper to check multiple indicators
        try:
            status = is_generation_complete_via_js()
            if status.get("probablyDone", False):
                print(f"✓ Generation appears complete after {elapsed:.1f} seconds")
                print(f"  - Stop button gone: {status.get('stopButtonGone', False)}")
                print(f"  - Stable response: {status.get('hasStableResponse', False)}")
                print(f"  - Not thinking: {status.get('notThinking', False)}")
                generation_completed = True
                break
        except Exception as js_err:
            # If JS detection fails, fall back to response container check
            try:
                # Try to find response container with content
                response_containers = page.query_selector_all('div.model-response-text')
                if response_containers and len(response_containers) > 0:
                    # If we find a response with content, check if it's still changing
                    old_text = response_containers[0].inner_text()
                    time.sleep(1)  # Wait briefly
                    new_text = response_containers[0].inner_text()
                    
                    # If text didn't change, assume generation is complete
                    if old_text == new_text and len(old_text) > 20:
                        print(f"✓ Response text stabilized after {elapsed:.1f} seconds - generation completed")
                        generation_completed = True
                        break
            except Exception as e:
                # Ignore errors checking response
                pass
        
        # Check for stable content as a backup exit condition
        try:
            response_containers = page.query_selector_all('div.model-response-text')
            if response_containers and len(response_containers) > 0:
                # Get text of first container
                all_text = response_containers[0].inner_text()
                
                # If we have substantial text, see if it's stable
                if len(all_text.strip()) > 5:  # Lower threshold for testing
                    old_text = all_text
                    time.sleep(1)
                    
                    # Check if content changed
                    new_containers = page.query_selector_all('div.model-response-text')
                    if new_containers and len(new_containers) > 0:
                        new_text = new_containers[0].inner_text()
                        
                        if old_text.strip() == new_text.strip():
                            stable_content_counter += 1
                            print(f"Content stable check #{stable_content_counter}")
                            if stable_content_counter >= 3:
                                print(f"✓ Response content stable for {stable_content_counter} checks - assuming complete")
                                generation_completed = True
                                break
                        else:
                            # Content changed, reset counter
                            if stable_content_counter > 0:
                                print(f"Content changed, resetting stability counter")
                            stable_content_counter = 0
        except Exception as e:
            print(f"Error in content stability check: {e}")
            
        # Brief wait before checking again
        time.sleep(wait_interval)
    
    if generation_completed:
        print(f"✓ Generation completed after {elapsed:.1f} seconds")
        page.screenshot(path=f"test_after_response_gen_{int(time.time())}.png")
    else:
        print("! Generation did not complete properly")

    print("====== TEST COMPLETED ======")


if __name__ == "__main__":
    test_dynamic_waiting()
