import os
import time
from playwright.sync_api import sync_playwright 
from src.data_handler import DataHandler
from src.automation import Automation
import random

# --- Configuration ---
DATASET_PATH = "data/data_sample_blank.xlsx"  # Change to your actual dataset file
PROMPT_PATH = "prompts/prompt.txt"
# Directory to store browser session data (cookies, login, etc.)
USER_DATA_DIR = os.path.abspath("chrome_user_data")
AI_STUDIO_URL = "https://aistudio.google.com/"
BATCH_SIZE = 10  # Reduced batch size for debugging

def main():
    """
    Debug version of the main function to diagnose response extraction issues.
    """
    # --- 1. Load Data and Prompt ---
    try:
        # Ensure data directory exists
        if not os.path.exists("data"):
            os.makedirs("data")
            print("Created 'data' directory")
        
        # Check if dataset file exists
        if not os.path.exists(DATASET_PATH):
            print(f"Warning: Dataset file '{DATASET_PATH}' not found.")
            print("Please create this file with at least a 'full_text' column before proceeding.")
            return

        data_handler = DataHandler(DATASET_PATH)
        with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    except Exception as e:
        print(f"Error during initial loading: {e}")
        return

    if data_handler.get_unprocessed_data_count() == 0:
        print("All data has already been processed. Nothing to do.")
        return

    # --- 2. Initialize Browser ---
    print("\n" + "="*70)
    print("DEBUG MODE - MANUAL LOGIN REQUIRED:")
    print("1. Please login manually in the browser window that opens")
    print("2. If you see 'Chrome is being controlled by automated test software', IGNORE it")
    print("3. We will only process ONE batch and then stop for diagnostics")
    print("="*70 + "\n")
    
    # Make sure Chrome user data directory exists
    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)
        print(f"Created Chrome user data directory at: {USER_DATA_DIR}")
    elif os.path.exists(os.path.join(USER_DATA_DIR, "Default")):
        print("Using existing Chrome profile.")
    
    # Create automation instance
    automation = Automation(user_data_dir=USER_DATA_DIR)
    automation.start_session(AI_STUDIO_URL)

    try:
        # Get a smaller batch for testing
        batches = data_handler.get_data_batches(BATCH_SIZE)
        
        if not batches:
            print("No data to process.")
            return
        
        current_batch = batches[0]
        
        print("\n" + "="*50)
        print(f"DEBUG MODE: Processing a single batch of {len(current_batch)} items")
        print("="*50)

        # --- Process a single batch and stop ---
        print("\nDEBUG MODE: Will only process one batch and stop")
        results = automation.process_batch(prompt_template, current_batch)
        
        # Check results
        if results:
            print(f"\n✅ SUCCESS: Got {len(results)} results from Gemini")
            print("\nFirst few results:")
            for i, (label, justification) in enumerate(results[:3]):
                print(f"{i+1}. {label} - {justification[:50]}...")
                
            # Save the results
            print("\nSaving results to Excel file...")
            # Safely get the start index for unprocessed data
            unprocessed_data = data_handler.df[data_handler.df['label'].isnull() | data_handler.df['justification'].isnull()]
            if not unprocessed_data.empty:
                start_index = unprocessed_data.index[0]
            else:
                # If all data is processed, start from the beginning to overwrite
                print("Warning: All data appears to be processed. Will overwrite from the beginning.")
                start_index = 0
                
            data_handler.update_and_save_data(results, start_index)
            print("Results saved successfully")
        else:
            print("\n❌ FAILURE: Could not extract any results from Gemini")
            print("Review the screenshot files to diagnose UI interaction issues")

    except Exception as e:
        print(f"\nA critical error occurred: {e}")
    finally:
        # --- Graceful Shutdown ---
        print("\nDebug session complete. Closing browser...")
        automation.close_session()
        print("Debug diagnostics finished.")

if __name__ == "__main__":
    main()
