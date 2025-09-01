import os
import time
from src.data_handler import DataHandler
from src.automation import Automation
from src.logger import Logger # <-- TAMBAHKAN INI
import random
from src.failed_row_handler import FailedRowHandler

# --- Configuration ---
DATASET_PATH = "data/data_sample_blank.xlsx"  # Change to your actual dataset file
PROMPT_PATH = "prompts/prompt.txt"
# Directory to store browser session data (cookies, login, etc.)
USER_DATA_DIR = os.path.abspath("chrome_user_data")
AI_STUDIO_URL = "https://aistudio.google.com/"
BATCH_SIZE = 100
REQUESTS_BEFORE_CLEAR = 5 # Clear history every 5 batches

def main():
    """
    Main function to orchestrate the data labeling automation process.
    """
    logger = Logger() # Start logging
    failed_handler = FailedRowHandler() 
    
    # --- 1. Load Data and Prompt ---
    try:
        # Pastikan direktori data ada
        if not os.path.exists("data"):
            os.makedirs("data")
            print("Created 'data' directory")
        
        # Verifikasi file dataset yang digunakan
        print(f"INFO: Using dataset file: {os.path.abspath(DATASET_PATH)}")
        
        # Cek apakah dataset.xlsx sudah ada
        if not os.path.exists(DATASET_PATH):
            print(f"Warning: Dataset file '{DATASET_PATH}' not found.")
            print("Please create this file with at least a 'full_text' column before proceeding.")
            return
            
        # Menampilkan informasi file
        file_stats = os.stat(DATASET_PATH)
        print(f"INFO: File size: {file_stats.st_size} bytes")
        print(f"INFO: Last modified: {time.ctime(file_stats.st_mtime)}")

        data_handler = DataHandler(DATASET_PATH)
        with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    except Exception as e:
        print(f"Error during initial loading: {e}")
        return

    unprocessed_count = data_handler.get_unprocessed_data_count()
    if unprocessed_count == 0:
        print("All data has already been processed. Nothing to do.")
        return
    else:
        print(f"Found {unprocessed_count} unprocessed rows to process. Continuing with automation.")
        # Optional: Add a confirmation prompt if desired
        # confirm = input("Press Enter to continue or Ctrl+C to cancel...")
        print("Starting browser automation...")

    # --- 2. Initialize Browser ---
    print("\n" + "="*70)
    print("MENGATASI MASALAH LOGIN:")
    print("1. Anda harus login secara manual di browser yang akan terbuka")
    print("2. JIKA mendapat pesan 'Chrome is being controlled by automated test software':")
    print("   - ABAIKAN pesan tersebut (jangan klik 'Restore Chrome')")
    print("   - Terus lanjutkan proses login seperti biasa")
    print("3. JIKA mendapat pesan 'Couldn't sign you in':")
    print("   - Coba klik 'Try again'")
    print("   - Jika masih gagal, coba tutup script ini (Ctrl+C), hapus folder 'chrome_user_data',")
    print("     dan jalankan kembali script")
    print("="*70 + "\n")
    
    # Pastikan direktori untuk data Chrome ada
    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)
        print(f"Created Chrome user data directory at: {USER_DATA_DIR}")
    elif os.path.exists(os.path.join(USER_DATA_DIR, "Default")):
        print("Using existing Chrome profile. If login fails, consider deleting 'chrome_user_data' folder.")
    
    # Buat instance Automation dengan Chrome yang sudah terpasang
    automation = Automation(user_data_dir=USER_DATA_DIR)
    automation.start_session(AI_STUDIO_URL)

    request_count = 0
    
    try:
        # Get the index of the first unprocessed row - safely
        unprocessed_data = data_handler.df[data_handler.df['label'].isnull() | data_handler.df['justification'].isnull()]
        if not unprocessed_data.empty:
            unprocessed_start_index = unprocessed_data.index[0]
        else:
            # If all data is processed, start from the beginning to overwrite
            print("Warning: All data appears to be processed. Will overwrite from the beginning.")
            unprocessed_start_index = 0
        
        while data_handler.get_unprocessed_data_count() > 0:
            # --- 3. Get Next Batch ---
            batches = data_handler.get_data_batches(BATCH_SIZE)
            
            if not batches:
                print("No more data to process.")
                break
            
            current_batch = batches[0]
            
            print("\n" + "="*50)
            print(f"Processing batch of {len(current_batch)} items. "
                  f"Starting from original index {unprocessed_start_index}.")
            print(f"Remaining items to process: {data_handler.get_unprocessed_data_count()}")
            print("="*50)

            # --- 5. Process Batch with Retry Logic ---
            # Ambil teks asli dari batch untuk penanganan kegagalan
            unprocessed_df = data_handler.df[data_handler.df['label'].isnull() | data_handler.df['justification'].isnull()]
            original_texts_batch = unprocessed_df['full_text'].iloc[:len(current_batch)].tolist()
            
            max_retries = 3
            batch_to_process = current_batch
            
            for attempt in range(max_retries):
                print(f"\nProcessing attempt {attempt + 1} of {max_retries} for this batch.")
                
                results = automation.process_batch(prompt_template, batch_to_process)

                # Pisahkan hasil yang valid dan yang tidak valid
                valid_results = {} # Gunakan dict untuk melacak berdasarkan teks asli
                invalid_items_indices = []
                
                # Cek jika jumlah hasil tidak cocok, anggap semua gagal dan coba lagi
                if len(results) != len(batch_to_process):
                    print(f"Warning: Result count mismatch. Expected {len(batch_to_process)}, got {len(results)}. Retrying entire batch.")
                    if attempt < max_retries - 1:
                        # Kosongkan batch_to_process agar tidak ada yang diproses lebih lanjut di iterasi ini
                        batch_to_process = [] 
                        # Lanjutkan ke iterasi coba ulang berikutnya
                        continue
                    else:
                        print("Max retries reached due to result count mismatch. Marking all as failed.")
                        # Tandai semua item di batch ini sebagai gagal
                        for i in range(len(batch_to_process)):
                           original_text = original_texts_batch[i] # Dapatkan teks asli
                           failed_handler.add_failed_row(original_text, "ERROR", "Result count mismatch", "API Error")
                        # Hentikan loop coba ulang
                        break

                for i, result_tuple in enumerate(results):
                    label = result_tuple[0]
                    original_text = batch_to_process[i] # Teks yang dikirim di percobaan ini
                    
                    if label == "INVALID_LABEL":
                        invalid_items_indices.append(i)
                        invalid_label_received = result_tuple[2] # Ambil label salah dari tuple
                        print(f"Validation failed for item: '{original_text[:30]}...'. Invalid Label: '{invalid_label_received}'")
                    else:
                        valid_results[original_text] = (label, result_tuple[1])

                # Jika ada item yang tidak valid, siapkan untuk coba ulang
                if invalid_items_indices:
                    print(f"Found {len(invalid_items_indices)} items with invalid labels. Preparing for retry.")
                    
                    # Buat batch baru hanya dengan item yang gagal
                    batch_to_process = [batch_to_process[i] for i in invalid_items_indices]
                    
                    if attempt == max_retries - 1:
                        print("Max retries reached. Logging invalid items to failed file.")
                        for i in invalid_items_indices:
                            original_text = batch_to_process[i]
                            # Ambil hasil yang salah dari `results`
                            invalid_result = results[i]
                            failed_handler.add_failed_row(original_text, invalid_result[2], invalid_result[1], "Invalid Label")
                else:
                    print("All items in the batch are valid. Proceeding.")
                    batch_to_process = [] # Kosongkan batch untuk menghentikan loop retry
                
                # Jika batch untuk diproses sudah kosong, hentikan loop retry
                if not batch_to_process:
                    break
            
            # --- Susun ulang hasil akhir dan simpan ---
            final_results_for_saving = []
            for text in original_texts_batch:
                if text in valid_results:
                    final_results_for_saving.append(valid_results[text])
                else:
                    # Tandai baris yang gagal di Excel agar tidak diproses lagi
                    final_results_for_saving.append(("FAILED_VALIDATION", "See failed_labeled.xlsx"))
            
            data_handler.update_and_save_data(final_results_for_saving, unprocessed_start_index)
    
            # --- 6. Update and Save Data ---
            data_handler.update_and_save_data(results, unprocessed_start_index)
            request_count += 1

            # --- 7. Clear History Periodically ---
            if request_count % REQUESTS_BEFORE_CLEAR == 0:
                print("\n--- Clearing chat history to save memory ---")
                automation.clear_chat_history()
            
            # A small delay between batches to be polite to the server
            # time.sleep(10)
            inter_batch_delay = random.uniform(15, 25) # Jeda acak antara 15 dan 25 detik
            print(f"\nWaiting for {inter_batch_delay:.2f} seconds before the next batch...")
            time.sleep(inter_batch_delay)

    except Exception as e:
        print(f"\nA critical error occurred in the main loop: {e}")
    finally:
        # --- 8. Graceful Shutdown ---
        automation.close_session()
        
        # Explicitly release DataHandler resources to free file handles
        if 'data_handler' in locals() and data_handler:
            try:
                print("Releasing data handler resources...")
                data_handler.close()
            except Exception as close_err:
                print(f"Warning: Error closing data handler: {close_err}")
                
        print("\nAutomation finished.")
        logger.close()

if __name__ == "__main__":
    main()