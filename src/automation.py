import os
import re
import time
from typing import List, Tuple
from playwright.sync_api import sync_playwright, expect
import random

class Automation:
    """
    Handles browser automation tasks for interacting with AI Studio using Playwright.
    Uses a persistent browser context to maintain login sessions.
    """
    def __init__(self, user_data_dir: str):
        """
        Initializes the browser automation by launching a persistent context.
        This uses the locally installed Google Chrome and a dedicated user data directory
        to maintain login sessions and appear as a regular user.

        Args:
            user_data_dir (str): Path to a directory for storing browser session data.
        """
        self.playwright = sync_playwright().start()
        
        # Define a realistic user agent to avoid detection
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        
        # Create or ensure the directory exists
        os.makedirs(user_data_dir, exist_ok=True)
        
        # Launch with anti-detection measures
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            channel="chrome",  # Use the installed Google Chrome browser
            slow_mo=150,       # Slightly slower interactions, more human-like
            user_agent=user_agent,
            viewport={"width": 1280, "height": 800},  # Standard screen resolution
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',  # Critical: disables webdriver flag
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials'
            ]
        )
        
        # A persistent context might already have a page open.
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()
        
        # Set a default timeout for all actions to prevent script from hanging indefinitely
        self.page.set_default_timeout(60000) # 60 seconds

    def _apply_stealth_techniques(self):
        """
        Apply various techniques to make the browser appear more human-like
        and avoid detection as an automated browser.
        """
        # Hide automation-related flags and properties in the navigator object
        js_script = """
        // Pass webdriver check
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });

        // Pass chrome check
        window.chrome = {
            runtime: {},
        };

        // Pass notifications check
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Overwrite the `plugins` property to use a custom getter
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // Overwrite the `languages` property to use a custom getter
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        """
        
        try:
            self.page.evaluate(js_script)
            print("Applied browser fingerprinting countermeasures.")
        except Exception as e:
            print(f"Warning: Could not apply stealth techniques: {e}")
            
    def set_model_to_gemini_pro(self):
        """
        Sets the AI model to Gemini 2.5 Pro if it's available.
        This function uses a direct approach with DOM inspection to select Gemini 2.5 Pro.
        """
        try:
            print("Attempting to set model to Gemini 2.5 Pro using DOM inspection...")
            
            # Ambil screenshot awal
            self.page.screenshot(path=f"start_model_selection_{int(time.time())}.png")
            
            # Inspect the DOM to understand the structure of the page
            print("Inspecting DOM structure...")
            dom_info = self.page.evaluate("""() => {
                // Get information about the Run settings button
                const runSettingsButtons = Array.from(document.querySelectorAll('button'))
                    .filter(btn => btn.textContent && btn.textContent.includes('Run settings'));
                
                // Get information about model selection elements
                const modelElements = Array.from(document.querySelectorAll('*'))
                    .filter(el => {
                        const text = el.textContent;
                        return text && (
                            text.includes('Gemini 2.5 Flash') || 
                            text.includes('model-selector') || 
                            text.includes('Model:')
                        );
                    })
                    .map(el => ({
                        tagName: el.tagName,
                        className: el.className,
                        id: el.id,
                        text: el.textContent,
                        isVisible: el.offsetParent !== null,
                        rect: el.getBoundingClientRect()
                    }));
                
                return {
                    runSettingsInfo: runSettingsButtons.length > 0 ? {
                        exists: true,
                        className: runSettingsButtons[0].className,
                        rect: runSettingsButtons[0].getBoundingClientRect()
                    } : { exists: false },
                    modelElements: modelElements
                };
            }""")
            
            # Log the DOM information for debugging
            print(f"DOM inspection results: {dom_info}")
            
            # Step 1: Click Run settings button by coordinates if possible
            run_settings_button = self.page.locator('button:has-text("Run settings")')
            if run_settings_button.count() > 0:
                print("Found Run settings button. Clicking...")
                # Click at the center of the button
                run_settings_button.first.click()
                time.sleep(2)
                
                # Take screenshot after clicking Run settings
                self.page.screenshot(path=f"after_run_settings_click_{int(time.time())}.png")
                
                # Now analyze the settings panel that should be open
                panel_info = self.page.evaluate("""() => {
                    // Find all elements that might be part of the model selection UI
                    const allPossibleElements = Array.from(document.querySelectorAll('*'));
                    
                    // Look for the model card/dropdown/selection area
                    const modelSelectors = allPossibleElements.filter(el => {
                        const text = el.textContent;
                        return text && (
                            text.includes('Gemini 2.5 Flash') || 
                            text.includes('Image Preview')
                        );
                    }).map(el => ({
                        tagName: el.tagName,
                        className: el.className,
                        id: el.id,
                        text: el.textContent,
                        isVisible: el.offsetParent !== null,
                        rect: el.getBoundingClientRect(),
                        hasClickHandler: el.onclick !== null || 
                                        el.getAttribute('role') === 'button' ||
                                        el.tagName === 'BUTTON'
                    }));
                    
                    return {
                        modelSelectors
                    };
                }""")
                
                print(f"Settings panel analysis: {panel_info}")
                
                # Use a very direct method - click on the area where the model selector should be
                # based on the screenshot provided by the user
                if panel_info and 'modelSelectors' in panel_info and len(panel_info['modelSelectors']) > 0:
                    visible_selectors = [s for s in panel_info['modelSelectors'] if s['isVisible']]
                    if visible_selectors:
                        # Sort by y-position to get the topmost element which is likely the model selector
                        visible_selectors.sort(key=lambda s: s['rect']['y'])
                        target = visible_selectors[0]
                        
                        # Click on this element
                        print(f"Clicking on element: {target}")
                        x = target['rect']['x'] + target['rect']['width'] / 2
                        y = target['rect']['y'] + target['rect']['height'] / 2
                        self.page.mouse.click(x, y)
                        time.sleep(2)
                        
                        # Take screenshot after clicking model selector
                        self.page.screenshot(path=f"after_model_selector_click_{int(time.time())}.png")
                        
                        # Now look for Gemini 2.5 Pro in the dropdown that should have appeared
                        dropdown_info = self.page.evaluate("""() => {
                            // Find all elements that might contain "Gemini 2.5 Pro"
                            const allElements = Array.from(document.querySelectorAll('*'));
                            const geminiProElements = allElements.filter(el => {
                                const text = el.textContent;
                                return text && text.includes('Gemini 2.5 Pro');
                            }).map(el => ({
                                tagName: el.tagName,
                                className: el.className,
                                id: el.id,
                                text: el.textContent,
                                isVisible: el.offsetParent !== null,
                                rect: el.getBoundingClientRect()
                            }));
                            
                            return {
                                geminiProElements
                            };
                        }""")
                        
                        print(f"Dropdown analysis: {dropdown_info}")
                        
                        # Try to click on Gemini 2.5 Pro if found
                        if dropdown_info and 'geminiProElements' in dropdown_info and len(dropdown_info['geminiProElements']) > 0:
                            visible_options = [o for o in dropdown_info['geminiProElements'] if o['isVisible']]
                            if visible_options:
                                # Click on the first visible option
                                target = visible_options[0]
                                print(f"Clicking on Gemini 2.5 Pro element: {target}")
                                x = target['rect']['x'] + target['rect']['width'] / 2
                                y = target['rect']['y'] + target['rect']['height'] / 2
                                self.page.mouse.click(x, y)
                                time.sleep(2)
                                print("Successfully clicked on Gemini 2.5 Pro option!")
                                
                                # Final screenshot after clicking Gemini 2.5 Pro
                                self.page.screenshot(path=f"after_gemini_pro_click_{int(time.time())}.png")
                            else:
                                print("No visible Gemini 2.5 Pro elements found in dropdown.")
                        else:
                            print("No Gemini 2.5 Pro elements found in dropdown.")
                            
                            # Try one more approach - use keyboard navigation
                            print("Trying keyboard navigation...")
                            # Press down arrow several times to navigate through options
                            for _ in range(5):  # Try 5 times to find the right option
                                self.page.keyboard.press('ArrowDown')
                                time.sleep(0.5)
                                self.page.screenshot(path=f"keyboard_nav_{int(time.time())}.png")
                                
                                # Check if we've highlighted Gemini 2.5 Pro
                                highlight_info = self.page.evaluate("""() => {
                                    const highlighted = Array.from(document.querySelectorAll('*'))
                                        .filter(el => {
                                            const style = window.getComputedStyle(el);
                                            const text = el.textContent;
                                            return text && 
                                                   text.includes('Gemini 2.5 Pro') && 
                                                   (style.backgroundColor !== 'transparent' || 
                                                    style.backgroundColor !== 'rgba(0, 0, 0, 0)');
                                        });
                                    return highlighted.length > 0;
                                }""")
                                
                                if highlight_info:
                                    # We found the highlighted Gemini 2.5 Pro option, press Enter
                                    self.page.keyboard.press('Enter')
                                    time.sleep(1)
                                    print("Selected Gemini 2.5 Pro using keyboard navigation!")
                                    break
                    else:
                        print("No visible model selector elements found.")
                else:
                    print("No model selector elements found in settings panel.")
            else:
                print("Run settings button not found.")
            
            # Final fallback - direct JavaScript execution
            print("Attempting direct JavaScript model selection...")
            try:
                self.page.evaluate("""() => {
                    // This is a more aggressive approach to find and click elements
                    
                    // Helper function to click an element
                    function simulateClick(element) {
                        const event = new MouseEvent('click', {
                            view: window,
                            bubbles: true,
                            cancelable: true
                        });
                        element.dispatchEvent(event);
                    }
                    
                    // Step 1: Click the Run settings if not already clicked
                    const runSettingsButtons = Array.from(document.querySelectorAll('button'))
                        .filter(btn => btn.textContent && btn.textContent.includes('Run settings'));
                    if (runSettingsButtons.length > 0) {
                        simulateClick(runSettingsButtons[0]);
                        console.log("Clicked Run settings via JavaScript");
                        
                        // Wait a bit for the panel to open
                        setTimeout(() => {
                            // Step 2: Find and click the model selector
                            const modelSelectors = Array.from(document.querySelectorAll('*'))
                                .filter(el => {
                                    const text = el.textContent;
                                    return text && text.includes('Gemini 2.5 Flash');
                                });
                            
                            if (modelSelectors.length > 0) {
                                simulateClick(modelSelectors[0]);
                                console.log("Clicked model selector via JavaScript");
                                
                                // Wait a bit for the dropdown to open
                                setTimeout(() => {
                                    // Step 3: Find and click Gemini 2.5 Pro
                                    const geminiProOptions = Array.from(document.querySelectorAll('*'))
                                        .filter(el => {
                                            const text = el.textContent;
                                            return text && text.includes('Gemini 2.5 Pro');
                                        });
                                    
                                    if (geminiProOptions.length > 0) {
                                        simulateClick(geminiProOptions[0]);
                                        console.log("Clicked Gemini 2.5 Pro via JavaScript");
                                        return true;
                                    } else {
                                        console.log("No Gemini 2.5 Pro options found");
                                        return false;
                                    }
                                }, 1000);
                            } else {
                                console.log("No model selectors found");
                                return false;
                            }
                        }, 1000);
                    } else {
                        console.log("No Run settings button found");
                        return false;
                    }
                }""")
                time.sleep(3)  # Give time for the JavaScript to execute
                
                # Final screenshot
                self.page.screenshot(path=f"after_javascript_direct_{int(time.time())}.png")
                
            except Exception as js_err:
                print(f"JavaScript direct execution failed: {js_err}")
                
        except Exception as e:
            print(f"Error during model selection: {e}")
            self.page.screenshot(path=f"model_selection_error_{int(time.time())}.png")
            print("Continuing with default model...")

    def start_session(self, url: str):
        """
        Navigates to the specified URL and waits for the main UI to be ready.
        If the page is already on the correct URL, it just waits for the input box.
        """
        print(f"Ensuring browser is at {url}...")
        
        # Apply techniques to avoid detection as a bot
        self._apply_stealth_techniques()
        
        # Random wait between actions to appear more human-like
        time.sleep(1.5)
        
        # Only navigate if not already on a similar URL
        if "aistudio.google.com" not in self.page.url:
            print(f"Navigating to {url}...")
            self.page.goto(url, wait_until="domcontentloaded", timeout=90000)
            # Random wait after page load
            time.sleep(2.5)

        print("Page loaded. Waiting for AI Studio to become ready...")
        # Wait for the main input textbox to be visible, indicating the UI is ready.
        # This also serves as a check for successful login.
        try:
            # Menggunakan locator yang lebih andal untuk menunggu elemen muncul DAN terlihat
            print("Waiting for the input textarea to be visible...")
            # Selector ini lebih spesifik: cari textarea di dalam komponen ms-chunk-input
            input_locator = self.page.locator('ms-chunk-input textarea') 
            
            # Tunggu hingga elemen tersebut terlihat di halaman, maksimal 3 menit
            input_locator.wait_for(state="visible", timeout=180000)
            
            # Ambil screenshot tampilan awal untuk debugging
            try:
                self.page.screenshot(path=f"before_model_selection_{int(time.time())}.png")
            except Exception as ss_err:
                print(f"Could not take before screenshot: {ss_err}")
            
            # Periksa apakah sudah menggunakan Gemini 2.5 Pro
            model_info = self.page.evaluate("""() => {
                // Find any elements that might indicate the current model
                const modelIndicators = Array.from(document.querySelectorAll('*'))
                    .filter(el => {
                        const text = el.textContent;
                        return text && (
                            text.includes('Gemini') || 
                            text.includes('model') ||
                            text.includes('Model:')
                        );
                    })
                    .map(el => ({
                        tagName: el.tagName,
                        className: el.className,
                        id: el.id,
                        text: el.textContent
                    }));
                
                // Check if any element contains "Gemini 2.5 Pro"
                const isPro = modelIndicators.some(el => 
                    el.text.includes('Gemini 2.5 Pro')
                );
                
                return {
                    indicators: modelIndicators,
                    isGemini25Pro: isPro
                };
            }""")
            
            print(f"Current model check: {model_info}")
            
            # Hanya coba ubah model jika belum menggunakan Gemini 2.5 Pro
            if model_info and not model_info.get('isGemini25Pro', False):
                # Metode 1: Coba dengan set_model_to_gemini_pro()
                print("Model is not Gemini 2.5 Pro. Attempting main method for model selection...")
                self.set_model_to_gemini_pro()
                time.sleep(2)
                
                # Metode 2: Coba dengan metode alternatif jika diperlukan
                print("Attempting alternative method for model selection...")
                self.try_alternative_model_selection()
            else:
                print("Already using Gemini 2.5 Pro model. No need to change.")
            
            # Ambil screenshot tampilan setelah pemilihan model
            try:
                self.page.screenshot(path=f"after_model_selection_{int(time.time())}.png")
            except Exception as ss_err:
                print(f"Could not take after screenshot: {ss_err}")
            
            print("AI Studio is ready.")
        except Exception as e:
            print("\n" + "="*70)
            print("MASALAH TIMEOUT ATAU LOGIN TERDETEKSI:")
            print(f"Error detail: {e}") # Menampilkan detail error
            print("1. Skrip tidak dapat menemukan kotak input utama setelah 3 menit.")
            print("2. Pastikan Anda sudah login dan tidak ada pop-up/dialog yang menghalangi.")
            print("3. Periksa koneksi internet Anda.")
            print("4. Skrip akan mengambil screenshot layar saat ini sebagai 'timeout_screenshot.png'.")
            print("="*70)
            self.page.screenshot(path="timeout_screenshot.png") # Ambil screenshot saat gagal
            self.close_session()
            exit()

    def process_batch(self, prompt_template: str, batch_data: List[str]) -> List[Tuple[str, str]]:
        """
        Processes a single batch of data by sending it to the AI Studio.
        Enhanced with advanced response extraction methods and retry logic.
        
        Features:
        - Automatic handling of various error cases (internal errors, permission denied)
        - Progressive retry with increasing delays
        - Special handling for permission denied errors with longer cooldown periods
        - Multiple response extraction methods for maximum reliability
        - Adaptive batch size reduction for permission denied errors

        Args:
            prompt_template (str): The base prompt from 'prompt.txt'.
            batch_data (List[str]): A list of 'full_text' strings for the current batch.

        Returns:
            A list of (label, justification) tuples, or an empty list if all retries fail.
        """
        # Check if batch is too large and reduce it if needed
        original_batch_size = len(batch_data)
        
        # Use adaptive recommended size based on past success/failures
        if hasattr(self, 'last_successful_batch_size'):
            recommended_size = min(50, self.last_successful_batch_size)
        else:
            recommended_size = 50
            
        # If we've had repeated permission errors, be more conservative
        if hasattr(self, 'consecutive_permission_errors') and self.consecutive_permission_errors > 2:
            # More conservative if many failures
            recommended_size = min(recommended_size, 25)
            print(f"Using conservative batch size of {recommended_size} due to previous permission errors")
        
        if original_batch_size > recommended_size:
            print(f"Batch size {original_batch_size} may be too large for permission limitations, reducing to {recommended_size}")
            batch_data = batch_data[:recommended_size]

        # Combine the prompt template with the actual data for this batch.
        full_prompt = f"{prompt_template}\n\n" + "\n".join(f'"{text}"' for text in batch_data)
        
        # Add retry mechanism for handling "internal error" and other temporary failures
        max_retries = 3
        retry_count = 0
        permission_denied_detected = False
        
        # Track successful and failed batch sizes for adaptive sizing
        # Initialize as class variables if not already present
        if not hasattr(self, 'last_successful_batch_size'):
            self.last_successful_batch_size = 50  # Start with recommended size
        if not hasattr(self, 'consecutive_permission_errors'):
            self.consecutive_permission_errors = 0
        
        while retry_count < max_retries:
            internal_error_detected = False
            
            if retry_count > 0:
                print(f"\n===== RETRY ATTEMPT {retry_count} of {max_retries} =====")
                
                # Use longer delays for permission denied errors (which might be rate-limiting)
                if permission_denied_detected:
                    delay_time = 15 * retry_count  # Longer delay for permission issues
                    print(f"Permission denied detected previously. Using longer delay: {delay_time} seconds")
                else:
                    delay_time = 5 * retry_count  # Standard progressive delay
                    print(f"Waiting {delay_time} seconds before retrying...")
                    
                time.sleep(delay_time)
                
                # Refresh the page between retries
                try:
                    print("Refreshing page before retry...")
                    self.page.reload(wait_until="domcontentloaded")
                    time.sleep(5)
                    # Wait for input textarea to appear again
                    self.page.wait_for_selector('ms-chunk-input textarea', timeout=60000)
                    print("✓ Page refreshed successfully, ready for retry")
                except Exception as refresh_err:
                    print(f"! Warning: Could not refresh page: {refresh_err}")
            
            print(f"Processing a batch of {len(batch_data)} items...")
            print("--- DEBUG: Mencari kotak input ---")            # --- MORE ROBUST SELECTORS (August 2025) ---
            # Menargetkan textarea di dalam komponen input utamanya
            input_textbox_selector = 'ms-chunk-input textarea'
            # Menargetkan tombol Run yang berada di dalam footer untuk menghindari salah klik
            send_button_selector = 'footer button[aria-label="Run"]'
            # Selector ini kemungkinan masih valid, kita biarkan dulu
            response_container_selector = 'div.model-response-text' 
            # Selector ini juga kemungkinan masih valid
            stop_generating_selector = 'button:has-text("Stop")'

            human_like_delay = random.uniform(1.5, 3.5)
            print(f"Waiting for {human_like_delay:.2f} seconds to appear more human-like...")
            time.sleep(human_like_delay)

            # Pastikan textbox ada dan terlihat sebelum mengisi
            try:
                input_locator = self.page.locator(input_textbox_selector)
                input_locator.wait_for(state="visible", timeout=30000)
                print("Input textbox is ready.")
            except Exception as input_err:
                print(f"Warning: Issue with input textbox: {input_err}")
                # Coba refresh halaman dan tunggu lagi
                self.page.reload()
                time.sleep(5)
                input_locator = self.page.locator(input_textbox_selector)
                input_locator.wait_for(state="visible", timeout=60000)

            print("Pasting prompt into the textbox...")
            self.page.fill(input_textbox_selector, full_prompt)
            print("--- DEBUG: Berhasil mengisi prompt ---")
            
            # Pastikan tombol kirim ada dan terlihat sebelum mengklik
            try:
                send_locator = self.page.locator(send_button_selector)
                send_locator.wait_for(state="visible", timeout=10000)
                print("Send button is ready.")
            except Exception as send_err:
                print(f"Warning: Issue with send button: {send_err}")
                # Coba dengan selector alternatif
                send_button_selector = 'button:has-text("Run"), footer button'
                send_locator = self.page.locator(send_button_selector)
                send_locator.wait_for(state="visible", timeout=15000)
                
            print("Clicking the send button...")
            self.page.click(send_button_selector)
            print("--- DEBUG: Berhasil mengklik tombol kirim ---")
            
            print("Waiting for the response to be generated...")

            # Take screenshot before starting response generation
            self.page.screenshot(path=f"before_response_gen_{int(time.time())}.png")

            # Track generation status
            generation_started = False
            generation_completed = False
            error_detected = False

            # Enhanced debug information for response extraction
            print("====== DEBUG: Waiting for generation to start and complete ======")
            
            # Helper method to detect if generation is complete via JavaScript
            def is_generation_complete_via_js():
                try:
                    # This JS checks for generation completion by looking for indicators
                    result = self.page.evaluate("""() => {
                        // Check if stop button is gone
                        const stopButton = document.querySelector('button:has-text("Stop")');
                        const stopButtonGone = !stopButton || !stopButton.offsetParent;
                        
                        // Check if response container has stabilized content
                        const responseContainers = Array.from(document.querySelectorAll('div.model-response-text, div.response-content, .message.model'));
                        const hasStableResponse = responseContainers.some(el => el.textContent && el.textContent.length > 20);
                        
                        // Check for "model is thinking" indicator gone
                        const thinkingIndicators = Array.from(document.querySelectorAll('.thinking, .loading, .spinner, .dots-loader, [aria-busy="true"]'));
                        const notThinking = thinkingIndicators.every(el => !el.offsetParent);
                        
                        return {
                            stopButtonGone,
                            hasStableResponse,
                            notThinking,
                            // If 2 out of 3 conditions are met, we're likely done
                            probablyDone: (stopButtonGone && hasStableResponse) || 
                                         (stopButtonGone && notThinking) || 
                                         (hasStableResponse && notThinking)
                        };
                    }""")
                    return result
                except Exception as e:
                    print(f"! Error checking generation status via JS: {e}")
                    return {"probablyDone": False}

            # Wait for generation to start
            try:
                # Wait for stop button to appear as indication generation started
                print("Waiting for generation to start (looking for Stop button)...")
                try:
                    self.page.wait_for_selector(stop_generating_selector, timeout=30000, state="visible")
                    generation_started = True
                    print("✓ Generation started successfully (Stop button detected)")
                    self.page.screenshot(path=f"generation_started_{int(time.time())}.png")
                except Exception as start_err:
                    print(f"! Warning: Could not detect generation start via Stop button: {start_err}")
                    
                    # Try alternative method to detect if generation started
                    try:
                        # Check if any response container starts appearing or showing "thinking" indicators
                        detection_js_result = self.page.evaluate("""() => {
                            // Check for thinking indicators
                            const thinkingIndicators = document.querySelectorAll('.thinking, .loading, .spinner, .dots-loader, [aria-busy="true"]');
                            const hasThinkingIndicator = Array.from(thinkingIndicators).some(el => el.offsetParent !== null);
                            
                            // Check for response container that's empty/being filled
                            const responseContainers = document.querySelectorAll('div.model-response-text, div.response-content, .message.model');
                            const hasResponseContainer = responseContainers.length > 0;
                            
                            return {
                                hasThinkingIndicator,
                                hasResponseContainer
                            };
                        }""")
                        
                        if detection_js_result.get('hasThinkingIndicator') or detection_js_result.get('hasResponseContainer'):
                            print("✓ Generation appears to have started (detected response elements)")
                            generation_started = True
                    except Exception as detect_err:
                        print(f"! Error in alternative generation start detection: {detect_err}")
                    
                    # Check for error messages that might appear
                    error_selectors = [
                        '.mat-mdc-snack-bar-label', 
                        'div.toast', 
                        'div:has-text("Failed to generate")',
                        'div:has-text("permission denied")',
                        'div:has-text("Please try again")',
                        'div:has-text("An internal error has occurred")',
                        'div:has-text("internal error")',
                        'div:has-text("rate limit")',
                        'div.model-response-text:has-text("Failed to generate")',
                        'div.model-response-text:has-text("permission denied")',
                        'div.error-container',
                        'div.error-message',
                        '.error-toast',
                        'div[role="alert"]',
                        'div.gmat-mdc-snack-bar-label',
                        'div.mat-mdc-snack-bar-container',
                        'ms-toast-message div.message',
                        'div.model-response-text:has-text("internal error")',
                        'div.model-response-text:has-text("An internal error has occurred")',
                        'ms-message:has-text("permission denied")',
                        'ms-message-container:has-text("Failed to generate")'
                    ]
                    
                    # Check for errors via JavaScript for elements that might be hidden
                    try:
                        error_js_check = self.page.evaluate("""() => {
                            // Find all elements that might contain error messages
                            const allElements = Array.from(document.querySelectorAll('*'));
                            const errorElements = allElements.filter(el => {
                                const text = el.textContent || '';
                                return (text.includes('Failed to generate') || 
                                       text.includes('permission denied') ||
                                       text.includes('Please try again') ||
                                       text.includes('internal error') ||
                                       text.includes('An internal error has occurred') ||
                                       text.includes('rate limit') ||
                                       text.includes('error') && el.offsetParent !== null);
                            });
                            
                            if (errorElements.length > 0) {
                                return {
                                    found: true,
                                    text: errorElements[0].textContent,
                                    path: getElementPath(errorElements[0])
                                };
                            }
                            
                            // Helper to get DOM path for debugging
                            function getElementPath(element) {
                                let path = [];
                                while (element && element.nodeType === Node.ELEMENT_NODE) {
                                    let selector = element.nodeName.toLowerCase();
                                    if (element.id) {
                                        selector += '#' + element.id;
                                    } else if (element.className) {
                                        selector += '.' + element.className.replace(/ /g, '.');
                                    }
                                    path.unshift(selector);
                                    element = element.parentNode;
                                }
                                return path.join(' > ');
                            }
                            
                            return { found: false };
                        }""")
                        
                        if error_js_check and error_js_check.get('found', False):
                            error_content = error_js_check.get('text', '')
                            error_path = error_js_check.get('path', '')
                            print(f"! Found error via JavaScript: '{error_content}'")
                            print(f"! Error element path: {error_path}")
                            error_detected = True
                            
                            # Take a screenshot with a specific name based on error type
                            timestamp = int(time.time())
                            if 'permission denied' in error_content.lower():
                                self.page.screenshot(path=f"permission_denied_{timestamp}.png")
                                print("\n!!! PERMISSION DENIED ERROR DETECTED !!!")
                                print("This is a limitation from Google's AI service and not an issue with your code.")
                                print("Possible reasons:")
                                print(" - Content policy violation in your prompt or batch data")
                                print(" - Rate limits on the Gemini API")
                                print(" - Temporary service outage")
                                print("\nRecommendations:")
                                print(" - Try smaller batches of data")
                                print(" - Ensure your prompt doesn't contain sensitive content")
                                print(" - Add longer delays between requests")
                                print(" - Try again later when rate limits reset")
                                
                                # Set flag for permission denied detection to use longer delays on retry
                                permission_denied_detected = True
                            else:
                                self.page.screenshot(path=f"error_detected_{timestamp}.png")
                    except Exception as js_err:
                        print(f"! Error in JavaScript error check: {js_err}")
                    
                    # Also check via DOM selectors
                    for selector in error_selectors:
                        try:
                            if self.page.locator(selector).count() > 0:
                                error_content = self.page.locator(selector).first.inner_text()
                                print(f"! Found potential error element with content: '{error_content}'")
                                if any(term in error_content.lower() for term in ["fail", "error", "permission denied"]):
                                    print(f"! Error message confirmed: '{error_content}'")
                                    error_detected = True
                                    
                                    # Check if this is a permission denied error specifically
                                    if "permission denied" in error_content.lower():
                                        print("! Permission denied error detected via DOM element")
                                        permission_denied_detected = True
                                        self.page.screenshot(path=f"permission_denied_{int(time.time())}.png")
                                    else:
                                        self.page.screenshot(path=f"error_detected_{int(time.time())}.png")
                                    break
                        except Exception as e:
                            continue
                
                # If no errors found but also no stop button, assume generation started anyway
                if not generation_started and not error_detected:
                    print("? No Stop button found but no errors detected, assuming generation started")
                    generation_started = True
                
                # If generation started, wait for it to complete (dynamically)
                if generation_started and not error_detected:
                    print("Waiting for model to complete generation...")
                    print("Using dynamic waiting algorithm (monitors multiple completion indicators)")
                    
                    # First, make sure we can detect when Stop button disappears
                    stop_button_visible = False
                    try:
                        stop_button_count = self.page.locator(stop_generating_selector).count()
                        stop_button_visible = stop_button_count > 0
                        if stop_button_visible:
                            print("✓ Stop button is currently visible, will wait for it to disappear")
                        else:
                            print("? Stop button is not currently visible, will wait for response container")
                    except Exception as e:
                        print(f"? Could not check Stop button visibility: {e}")
                    
                    # Dynamic waiting strategy with safety measures
                    max_wait_time = 240  # Maximum seconds to wait (4 minutes)
                    min_wait_time = 20   # Minimum seconds to wait (prevent too early exit)
                    start_wait_time = time.time()
                    wait_interval = 2    # Check every 2 seconds
                    progress_shown = False
                    stable_content_counter = 0  # Count how many times content remains stable
                    last_progress_time = time.time()  # Track when last progress was made
                    
                    while True:
                        # Check if we've waited too long
                        elapsed = time.time() - start_wait_time
                        if elapsed > max_wait_time:
                            print(f"! Maximum wait time of {max_wait_time} seconds exceeded.")
                            print("! Proceeding anyway - response may be incomplete")
                            generation_completed = True
                            break
                            
                        # Ensure we don't exit too early, wait at least min_wait_time
                        if elapsed < min_wait_time:
                            if int(elapsed) % 5 == 0 and not progress_shown:
                                print(f"Initial waiting period... ({int(elapsed)}/{min_wait_time} seconds)")
                                progress_shown = True
                            elif int(elapsed) % 5 != 0:
                                progress_shown = False
                                
                        # Show waiting progress periodically
                        elif int(elapsed) % 10 == 0 and not progress_shown:
                            print(f"Still waiting for generation to complete... ({int(elapsed)} seconds)")
                            progress_shown = True
                        elif int(elapsed) % 10 != 0:
                            progress_shown = False
                            
                        # Safety check: if we've waited too long since last progress, exit
                        if elapsed > 60 and (time.time() - last_progress_time) > 60:
                            print("! No progress detected for 60 seconds, assuming generation is stuck or complete")
                            generation_completed = True
                            break
                            
                        # Strategy 1: If Stop button was visible, wait for it to disappear
                        if stop_button_visible:
                            try:
                                # Check if Stop button is still visible
                                new_count = self.page.locator(stop_generating_selector).count()
                                if new_count == 0:
                                    print(f"✓ Stop button disappeared after {elapsed:.1f} seconds - generation completed")
                                    generation_completed = True
                                    break
                            except Exception:
                                # Ignore errors checking button, continue waiting
                                pass
                        
                        # Strategy 2: Use our JavaScript helper to check multiple indicators
                        try:
                            status = is_generation_complete_via_js()
                            
                            # Update progress tracking
                            if status.get("hasStableResponse", False):
                                last_progress_time = time.time()
                            
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
                                response_container = self.page.locator('div.model-response-text').first
                                if response_container and response_container.inner_text().strip():
                                    # If we find a response with content, check if it's still changing
                                    current_text = response_container.inner_text()
                                    time.sleep(3)  # Wait briefly
                                    new_text = response_container.inner_text()
                                    
                                    # If text didn't change, assume generation is complete
                                    if current_text == new_text and len(current_text) > 20:
                                        print(f"✓ Response text stabilized after {elapsed:.1f} seconds - generation completed")
                                        generation_completed = True
                                        break
                            except Exception:
                                # Ignore errors checking response, continue waiting
                                pass
                        
                        # Check for stable content as a backup exit condition
                        try:
                            response_containers = self.page.query_selector_all('div.model-response-text, div.response-content, .message.model')
                            if response_containers and len(response_containers) > 0:
                                # Get combined text of all containers
                                all_text = ""
                                for container in response_containers:
                                    all_text += container.inner_text() + " "
                                
                                # If we have substantial text, see if it's stable
                                if len(all_text.strip()) > 50:
                                    old_text = all_text
                                    time.sleep(2)
                                    
                                    # Check if content changed
                                    new_containers = self.page.query_selector_all('div.model-response-text, div.response-content, .message.model')
                                    new_text = ""
                                    for container in new_containers:
                                        new_text += container.inner_text() + " "
                                    
                                    if old_text.strip() == new_text.strip():
                                        stable_content_counter += 1
                                        print(f"→ Content stability check #{stable_content_counter}/3")
                                        if stable_content_counter >= 3:
                                            print(f"✓ Response content stable for {stable_content_counter} checks - assuming complete")
                                            generation_completed = True
                                            break
                                    else:
                                        # Content changed, reset counter but update progress time
                                        if stable_content_counter > 0:
                                            print(f"→ Content still changing, resetting stability counter")
                                        stable_content_counter = 0
                                        last_progress_time = time.time() # Update progress time since content is changing
                        except Exception:
                            pass
                            
                        # Brief wait before checking again
                        time.sleep(wait_interval)
                    
                    print("✓ Dynamic waiting for generation completed")
                    # Take screenshot after response generation
                    self.page.screenshot(path=f"after_response_gen_{int(time.time())}.png")
                    generation_completed = True
                    
                    # Additional 3 second delay to ensure rendering completes
                    time.sleep(3)
                
                # Handle case where errors were detected
                if error_detected:
                    print("! ERROR: Permission denied or API error detected!")
                    print("! Attempting to capture what response might be visible anyway...")
                    self.page.screenshot(path=f"error_state_{int(time.time())}.png")
            except Exception as wait_err:
                print(f"! Warning: Error during response generation tracking: {wait_err}")
                self.page.screenshot(path=f"wait_error_{int(time.time())}.png")

            print("\n====== ADVANCED RESPONSE EXTRACTION ======")
            print("Attempting to extract response using multiple methods...")
            
            try:
                # Take initial screenshot to analyze the UI state
                debug_screenshot_path = f"response_extraction_{int(time.time())}.png"
                self.page.screenshot(path=debug_screenshot_path)
                print(f"✓ UI state screenshot saved to: {debug_screenshot_path}")
                
                # Define comprehensive list of potential response selectors
                response_selectors = [
                    # Primary selectors for Gemini UI
                    'div.model-response-text', 
                    'div.response-content',
                    'div.message-content',
                    'ms-message div',
                    '.message.model',
                    
                    # Alternative selectors based on common patterns
                    'div[role="region"]',
                    'div.ai-response',
                    'div.response',
                    '.response-container',
                    'div.chunk-node.code-chat',
                    '.response-message',
                    'ms-message-container .content'
                ]
                
                # METHOD 1: Try all selectors to find response elements
                print("METHOD 1: Trying direct DOM selectors...")
                all_responses = []
                used_selector = None
                
                for selector in response_selectors:
                    try:
                        elements = self.page.query_selector_all(selector)
                        if elements and len(elements) > 0:
                            all_responses = elements
                            used_selector = selector
                            print(f"✓ Found {len(elements)} response elements with selector: '{selector}'")
                            
                            # Print preview of each element's text
                            for i, elem in enumerate(elements):
                                text = elem.inner_text()
                                preview = text[:50] + "..." if len(text) > 50 else text
                                print(f"  Element {i+1}: '{preview}'")
                            break
                    except Exception as selector_err:
                        print(f"  Selector '{selector}' failed: {selector_err}")
                
                # METHOD 2: Use JavaScript to find response elements with key indicators
                print("\nMETHOD 2: Using JavaScript to scan for response elements...")
                response_text_js = None
                
                try:
                    # Advanced JavaScript approach to find elements containing our expected response format
                    response_text_js = self.page.evaluate("""() => {
                        // Look for elements with our expected response format (POSITIF, NEGATIF, NETRAL, etc.)
                        const allElements = Array.from(document.querySelectorAll('*'));
                        
                        // Check first for error messages
                        const errorElements = allElements.filter(el => {
                            const text = el.textContent || '';
                            return text.includes('internal error') || 
                                  text.includes('An internal error has occurred');
                        });
                        
                        if (errorElements.length > 0) {
                            console.log("Found internal error message:", errorElements[0].textContent);
                            return errorElements[0].textContent;
                        }
                        
                        // Then look for elements containing sentiment labels
                        const elementsWithLabels = allElements.filter(el => {
                            const text = el.textContent || '';
                            return text.includes('POSITIF') || 
                                  text.includes('NEGATIF') || 
                                  text.includes('NETRAL') || 
                                  text.includes('TIDAK RELEVAN');
                        });
                        
                        if (elementsWithLabels.length > 0) {
                            console.log("Found elements containing sentiment labels:", elementsWithLabels.length);
                            // Sort by text length (longer is likely the full response)
                            const sorted = elementsWithLabels.sort((a, b) => 
                                b.textContent.length - a.textContent.length);
                            return sorted[0].textContent;
                        }
                        
                        // Second try - look for visible elements with substantial text
                        const visibleTextElements = allElements.filter(el => {
                            const isVisible = el.offsetParent !== null;
                            const hasSubstantialText = el.textContent && el.textContent.length > 100;
                            const isNotInput = !el.querySelector('input, textarea, button');
                            return isVisible && hasSubstantialText && isNotInput;
                        });
                        
                        if (visibleTextElements.length > 0) {
                            console.log("Found visible elements with substantial text:", visibleTextElements.length);
                            // Sort by text length
                            const sorted = visibleTextElements.sort((a, b) => 
                                b.textContent.length - a.textContent.length);
                            return sorted[0].textContent;
                        }
                        
                        return null;
                    }""")
                    
                    if response_text_js:
                        print("✓ Found response via JavaScript method")
                        print(f"  Preview: '{response_text_js[:100]}...'")
                    else:
                        print("✗ JavaScript method could not find response elements")
                except Exception as js_err:
                    print(f"✗ JavaScript extraction error: {js_err}")
                
                # METHOD 3: DOM structure exploration to find all potential response content
                print("\nMETHOD 3: DOM structure exploration...")
                dom_exploration_result = None
                
                try:
                    dom_exploration_result = self.page.evaluate("""() => {
                        // Find all elements that might contain responses
                        const allElements = Array.from(document.querySelectorAll('div, p, span, ms-message'));
                        const potentialResponses = allElements
                            .filter(el => {
                                // Filter visible elements with substantial text
                                return el.offsetParent !== null && 
                                      el.textContent && 
                                      el.textContent.length > 50 && 
                                      !el.querySelector('textarea, input');
                            })
                            .map(el => ({
                                text: el.textContent,
                                tagName: el.tagName,
                                className: el.className,
                                id: el.id,
                                path: getElementPath(el)
                            }));
                        
                        // Helper to get DOM path
                        function getElementPath(element) {
                            let path = [];
                            while (element && element.nodeType === Node.ELEMENT_NODE) {
                                let selector = element.nodeName.toLowerCase();
                                if (element.id) {
                                    selector += '#' + element.id;
                                } else if (element.className) {
                                    selector += '.' + String(element.className).replace(/ /g, '.');
                                }
                                path.unshift(selector);
                                element = element.parentNode;
                            }
                            return path.join(' > ');
                        }
                        
                        return potentialResponses;
                    }""")
                    
                    if dom_exploration_result and len(dom_exploration_result) > 0:
                        print(f"✓ Found {len(dom_exploration_result)} potential response elements")
                        # Print the top 3 elements by text length
                        sorted_elements = sorted(dom_exploration_result, key=lambda x: len(x.get('text', '')), reverse=True)
                        for i, elem in enumerate(sorted_elements[:3]):
                            preview = elem.get('text', '')[:50] + "..." if len(elem.get('text', '')) > 50 else elem.get('text', '')
                            print(f"  Element {i+1}: {elem.get('tagName')} {elem.get('className')} - '{preview}'")
                            print(f"    Path: {elem.get('path')}")
                    else:
                        print("✗ DOM exploration found no potential response elements")
                except Exception as dom_err:
                    print(f"✗ DOM exploration error: {dom_err}")
                
                # Decide which method produced the best result
                print("\nFINAL RESPONSE EXTRACTION:")
                raw_response = None
                
                # First check if Method 1 worked (direct selectors)
                if all_responses:
                    print(f"✓ Using response from METHOD 1 (selector: '{used_selector}')")
                    # If multiple elements found, use the last one (often the most complete in streaming UI)
                    raw_response = all_responses[-1].inner_text()
                # Then check JavaScript method
                elif response_text_js:
                    print("✓ Using response from METHOD 2 (JavaScript)")
                    raw_response = response_text_js
                # Finally check DOM exploration method
                elif dom_exploration_result and len(dom_exploration_result) > 0:
                    print("✓ Using response from METHOD 3 (DOM exploration)")
                    # Use the element with the longest text content
                    sorted_elements = sorted(dom_exploration_result, key=lambda x: len(x.get('text', '')), reverse=True)
                    raw_response = sorted_elements[0].get('text', '')
                else:
                    print("✗ All extraction methods failed to find a response")
                    self.page.screenshot(path=f"extraction_failed_{int(time.time())}.png")
                    return []
                
                # Print the raw response for debugging
                print("\n" + "="*25 + " DEBUG: RAW RESPONSE " + "="*25)
                print(raw_response)
                print("="*70 + "\n")
                
                # If we got to this point but have no raw_response, try one final desperate approach
                if not raw_response:
                    print("\nEMERGENCY METHOD: Trying HTML content analysis...")
                    try:
                        # Get HTML content and analyze for potential response patterns
                        html_content = self.page.content()
                        
                        # Look for common response patterns in the HTML
                        response_patterns = [
                            r'(POSITIF.+?-.*?(?=POSITIF|NEGATIF|NETRAL|TIDAK RELEVAN|\n\n|\Z))',
                            r'(NEGATIF.+?-.*?(?=POSITIF|NEGATIF|NETRAL|TIDAK RELEVAN|\n\n|\Z))',
                            r'(NETRAL.+?-.*?(?=POSITIF|NEGATIF|NETRAL|TIDAK RELEVAN|\n\n|\Z))',
                            r'(TIDAK RELEVAN.+?-.*?(?=POSITIF|NEGATIF|NETRAL|TIDAK RELEVAN|\n\n|\Z))'
                        ]
                        
                        extracted_responses = []
                        for pattern in response_patterns:
                            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
                            extracted_responses.extend(matches)
                        
                        if extracted_responses:
                            raw_response = "\n".join(extracted_responses)
                            print(f"✓ EMERGENCY METHOD found {len(extracted_responses)} responses")
                            print(f"First response: '{extracted_responses[0][:50]}...'")
                        else:
                            print("✗ EMERGENCY METHOD found no response patterns in HTML")
                    except Exception as html_err:
                        print(f"✗ EMERGENCY HTML extraction error: {html_err}")
                
                # Final result
                if raw_response:
                    print("\n✓ SUCCESSFULLY extracted response text")
                    
                    # Check for internal error messages in the response
                    if "internal error" in raw_response.lower() or "an internal error has occurred" in raw_response.lower():
                        print("! Internal error detected in the response content")
                        self.page.screenshot(path=f"internal_error_{int(time.time())}.png")
                        internal_error_detected = True
                        
                        # Don't increment retry count yet - let the outer loop handle it
                        continue
                        
                    # Check for permission denied errors in the response
                    if "permission denied" in raw_response.lower() or "failed to generate" in raw_response.lower():
                        print("! Permission denied detected in the response content")
                        self.page.screenshot(path=f"permission_denied_{int(time.time())}.png")
                        internal_error_detected = True
                        permission_denied_detected = True
                        
                        # Don't increment retry count yet - let the outer loop handle it
                        continue
                    
                    # If no errors detected, parse the response
                    results = self._parse_response(raw_response, len(batch_data))
                    
                    # If we got results, return them
                    if results:
                        print(f"✓ Successfully parsed {len(results)} results")
                        
                        # Update adaptive batch sizing data
                        self.last_successful_batch_size = len(batch_data)
                        self.consecutive_permission_errors = 0
                        print(f"✓ Recorded successful batch size: {self.last_successful_batch_size} for future requests")
                        
                        return results
                    else:
                        print("! Response was extracted but no parsable results found")
                        # If we couldn't parse results, consider it an error and retry
                        internal_error_detected = True
                else:
                    print("\n✗ ALL EXTRACTION METHODS FAILED")
                    self.page.screenshot(path=f"all_extraction_failed_{int(time.time())}.png")
                    internal_error_detected = True
            
            except Exception as extract_err:
                print(f"!! Error extracting response: {extract_err}")
                self.page.screenshot(path=f"extraction_error_{int(time.time())}.png")
                internal_error_detected = True
            
            # If we detected an error, increment retry counter
            if internal_error_detected:
                retry_count += 1
                
                # If we got a permission denied error, make a special note and reduce batch size
                if permission_denied_detected:
                    print("\n! SPECIAL HANDLING: Permission denied error detected")
                    print(f"! Using longer delay between retries ({15 * retry_count} seconds on next attempt)")
                    
                    # Increment consecutive permission errors counter
                    self.consecutive_permission_errors += 1
                    
                    # Reduce recommended batch size for future batches
                    if self.consecutive_permission_errors >= 2:
                        self.last_successful_batch_size = max(5, self.last_successful_batch_size // 2)
                        print(f"! SYSTEM ADAPTATION: After {self.consecutive_permission_errors} consecutive permission errors, ")
                        print(f"  reducing future batch sizes to maximum of {self.last_successful_batch_size}")
                    
                    # Dynamic batch size reduction for permission denied errors
                    if len(batch_data) > 5:  # Don't go below 5 items
                        reduced_size = max(5, len(batch_data) // 2)  # Reduce by half, but minimum 5
                        print(f"! Reducing batch size from {len(batch_data)} to {reduced_size} due to permission denied")
                        batch_data = batch_data[:reduced_size]
                        # Recreate the prompt with the reduced batch
                        full_prompt = f"{prompt_template}\n\n" + "\n".join(f'"{text}"' for text in batch_data)
                
                if retry_count < max_retries:
                    print(f"Will retry ({retry_count}/{max_retries})...")
                    continue
                else:
                    print(f"! Maximum retries ({max_retries}) reached. Giving up.")
                    return []
        
        # If we've exhausted all retries or exited the loop without returning, fail gracefully
        print("! All attempts failed. Could not process batch.")
        return []

    def _parse_response(self, raw_response: str, expected_count: int) -> List[Tuple[str, str]]:
        """
        Parses the raw string response from the AI into a structured list of tuples.
        Uses a more robust parsing approach to handle various response formats.
        """
        VALID_LABELS = {'POSITIF', 'NEGATIF', 'NETRAL', 'TIDAK RELEVAN'}
        
        results = []
        lines = raw_response.strip().split('\n')
        print(f"Parsing {len(lines)} lines of response...")
        
        # Print first few lines of response for debugging
        preview_lines = min(5, len(lines))
        if preview_lines > 0:
            print("Response preview (first few lines):")
            for i in range(preview_lines):
                print(f"  {lines[i][:100]}...")
        
        # Check for internal error messages first
        internal_error_indicators = [
            "internal error", 
            "an internal error has occurred"
        ]
        
        for line in lines:
            if any(error in line.lower() for error in internal_error_indicators):
                print(f"Warning: Internal error message detected in response: '{line}'")
                print("This may cause problems with parsing. Results may be incomplete.")
                # We don't return early, as there might still be some valid responses we can extract
        
        # Define keywords that indicate a line is part of the prompt instructions, not a response
        prompt_indicators = [
            "tujuan", "prinsip utama", "kategori dan pedoman", "instruksi pelabelan", 
            "format output", "tugas anda", "completing", "progress", "analysis", 
            "klasifikasikan tweet", "label kategori", "negatif", "netral", "tidak relevan",
            "fokus inti", "konteks dan semantik", "deteksi buzzer", "definisi inti",
            "cakupan", "contoh tweet", "catatan buzzer", "spesifik vs. umum"
        ]
        
        # Step 1: Try using the expected format first
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines that are likely part of the instruction prompt
            if any(indicator in line.lower() for indicator in prompt_indicators):
                # Only if the line doesn't contain a valid label structure
                if not (' - ' in line or (line.startswith('[') and '] ' in line) or 
                       re.search(r'^\d+\.\s+(POSITIF|NEGATIF|NETRAL|TIDAK RELEVAN)\s+-\s+', line)):
                    print(f"Skipping likely prompt line: {line[:50]}...")
                    continue
            
            try:
                # Try primary format: "LABEL - Justification"
                if ' - ' in line:
                    parts = line.split(' - ', 1)
                    if len(parts) == 2:
                        label = parts[0].strip().upper() # <-- Konversi ke huruf besar
                        justification = parts[1].strip()
                        
                        # --- VALIDASI KETAT ---
                        if label in VALID_LABELS:
                            results.append((label, justification))
                        else:
                            # Tandai sebagai tidak valid agar bisa di-retry
                            results.append(("INVALID_LABEL", justification, label)) # <-- Kembalikan label asli yg salah
                        continue
                
                # Try alternative format: "[LABEL] [JUSTIFICATION]"
                if line.startswith('[') and '] ' in line:
                    parts = line.split('] ', 1)
                    if len(parts) == 2:
                        label = parts[0].strip('[')
                        justification = parts[1].strip()
                        
                        # Validate label
                        if label in ['POSITIF', 'NEGATIF', 'NETRAL', 'TIDAK RELEVAN']:
                            results.append((label, justification))
                            continue
                
                if line.startswith('[') and '] ' in line:
                    parts = line.split('] ', 1)
                    if len(parts) == 2:
                        label = parts[0].strip('[]').upper() # <-- Konversi ke huruf besar
                        justification = parts[1].strip()

                        if label in VALID_LABELS:
                            results.append((label, justification))
                        else:
                            results.append(("INVALID_LABEL", justification, label))
                        continue
                
                # Try numbered format: "1. LABEL - Justification"
                match = re.search(r'^\d+\.\s+(POSITIF|NEGATIF|NETRAL|TIDAK RELEVAN)\s+-\s+(.+)$', line)
                if match:
                    label = match.group(1)
                    justification = match.group(2)
                    results.append((label, justification))
                    continue
                
                print(f"Warning: Could not parse line: '{line}'")
            except Exception as e:
                print(f"Warning: Error parsing line '{line}': {e}")
        
        # This check is crucial for the retry logic.
        if len(results) != expected_count:
            print(f"Warning: Mismatch in response count. Expected {expected_count}, but got {len(results)}.")
            
            # If we got zero results but have lines in the response, try a more aggressive approach
            if len(results) == 0 and len(lines) > 0:
                print("Attempting more aggressive parsing as no valid results were found...")
                
                # Try to extract any lines containing our label keywords that seem to be actual responses
                for line in lines:
                    line = line.strip()
                    # Skip empty lines or very short lines
                    if not line or len(line) < 10:
                        continue
                        
                    # Skip lines that are clearly part of the prompt instructions
                    prompt_indicators = [
                        "tujuan", "prinsip utama", "kategori", "instruksi", "format output", 
                        "tugas anda", "completing", "progress", "analysis", "fokus inti", 
                        "konteks dan semantik", "deteksi buzzer", "definisi inti", 
                        "cakupan:", "contoh tweet:", "catatan buzzer"
                    ]
                    
                    if any(indicator in line.lower() for indicator in prompt_indicators):
                        continue
                    
                    # Only process lines that appear to be responses (contain a tweet or label pattern)
                    if "tweet:" in line.lower() or re.search(r'^\d+\.', line) or "label:" in line.lower():
                        for label in ['POSITIF', 'NEGATIF', 'NETRAL', 'TIDAK RELEVAN']:
                            if label in line:
                                # Extract everything after the label as justification
                                parts = line.split(label, 1)
                                if len(parts) > 1:
                                    justification = parts[1].strip()
                                    if justification.startswith('-'):
                                        justification = justification[1:].strip()
                                    results.append((label, justification))
                                    break
                
                print(f"After aggressive parsing, found {len(results)} results.")
        
        # Print a summary of what was actually extracted
        if results:
            print("\nFirst few results:")
            for i, (label, justification) in enumerate(results[:3]):
                preview = justification[:30] + "..." if len(justification) > 30 else justification
                print(f"{i+1}. {label} - {preview}")
        else:
            print("No valid results could be parsed from the response.")
                
        return results

    def clear_chat_history(self):
        """
        Clears the chat history by clicking the "Chat" link in the navigation.
        """
        try:
            print("Clearing chat history by starting a new chat...")
            # UPDATED SELECTOR: Targets the link (<a>) with class 'nav-item' containing the text "Chat"
            new_chat_button_selector = 'a.nav-item:has-text("Chat")'
            
            new_chat_locator = self.page.locator(new_chat_button_selector)
            
            # Check if the button is visible before clicking
            if new_chat_locator.is_visible():
                new_chat_locator.click()
                # Wait for the input box of the new chat to appear and be ready
                self.page.locator('ms-chunk-input textarea').wait_for(state="visible", timeout=60000)
                time.sleep(2) # Allow time for the new chat environment to stabilize.
                print("New chat started, history is cleared.")
            else:
                print("Warning: 'New chat' button not found. Refreshing page as an alternative.")
                self.page.reload(wait_until="domcontentloaded")
                self.page.locator('ms-chunk-input textarea').wait_for(state="visible", timeout=60000)

        except Exception as e:
            print(f"Could not clear chat history: {e}. Attempting a page reload.")
            self.page.reload(wait_until="domcontentloaded")
            self.page.locator('ms-chunk-input textarea').wait_for(state="visible", timeout=60000)


    def try_alternative_model_selection(self):
        """
        Alternative approach to select the Gemini 2.5 Pro model using browser-specific techniques.
        This is called if the primary method fails.
        """
        try:
            print("Trying alternative approach for model selection...")
            
            # Gunakan pendekatan dengan manipulasi URL langsung
            current_url = self.page.url
            print(f"Current URL: {current_url}")
            
            # Banyak web app menyimpan preferensi model dalam URL parameters atau path
            # Coba navigasi langsung ke URL yang mungkin dengan model Gemini 2.5 Pro
            if "aistudio.google.com" in current_url:
                # Coba tambahkan parameter atau path yang mengindikasikan Gemini 2.5 Pro
                # Contoh: ?model=gemini-2.5-pro atau /model/gemini-2.5-pro
                modified_url = current_url
                if "?" in modified_url:
                    modified_url += "&model=gemini-2.5-pro"
                else:
                    modified_url += "?model=gemini-2.5-pro"
                
                print(f"Attempting to navigate to URL with model parameter: {modified_url}")
                self.page.goto(modified_url, wait_until="domcontentloaded")
                time.sleep(3)
                
                # Tambahan: Coba inject local storage atau session storage
                print("Injecting storage preferences...")
                self.page.evaluate("""() => {
                    // Coba set localStorage
                    try {
                        localStorage.setItem('selectedModel', 'gemini-2.5-pro');
                        localStorage.setItem('preferredModel', 'gemini-2.5-pro');
                        console.log('Set localStorage preferences');
                    } catch (e) {
                        console.error('Failed to set localStorage:', e);
                    }
                    
                    // Coba set sessionStorage
                    try {
                        sessionStorage.setItem('selectedModel', 'gemini-2.5-pro');
                        sessionStorage.setItem('aiStudioModel', 'gemini-2.5-pro');
                        console.log('Set sessionStorage preferences');
                    } catch (e) {
                        console.error('Failed to set sessionStorage:', e);
                    }
                    
                    // Coba set cookie
                    try {
                        document.cookie = 'preferredModel=gemini-2.5-pro; path=/';
                        console.log('Set model preference cookie');
                    } catch (e) {
                        console.error('Failed to set cookie:', e);
                    }
                }""")
            
            # Tunggu elemen input muncul kembali setelah manipulasi
            input_locator = self.page.locator('ms-chunk-input textarea')
            input_locator.wait_for(state="visible", timeout=30000)
            
            print("Alternative method completed.")
            
            # Ambil screenshot hasil pendekatan alternatif
            self.page.screenshot(path=f"after_alternative_method_{int(time.time())}.png")
            
        except Exception as e:
            print(f"Alternative model selection method failed: {e}")
    
    def close_session(self):
        """
        Closes the browser context gracefully.
        """
        print("Closing browser session.")
        self.context.close()
        self.playwright.stop()

# Akhir file