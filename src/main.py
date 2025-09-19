import argparse
import logging
from pathlib import Path
import time
from datetime import datetime

# Impor komponen inti dari folder core_logic
# Pastikan Anda sudah memindahkan dan merefaktor file-file ini
try:
    from core_logic.data_handler import DataHandler
    from core_logic.browser_automation import Automation
    from core_logic.failed_row_handler import FailedRowHandler
    from core_logic.validation import parse_and_validate
    from core_logic.metrics_tracker import ExecutionMetricsTracker
except ImportError as e:
    import os
    import sys
    # Try to add current directory to path and retry
    if str(Path(__file__).parent) not in sys.path:
        sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from core_logic.data_handler import DataHandler
        from core_logic.browser_automation import Automation
        from core_logic.failed_row_handler import FailedRowHandler
        from core_logic.validation import parse_and_validate
        from core_logic.metrics_tracker import ExecutionMetricsTracker
    except ImportError:
        if os.getenv("TESTING") != "1":  # Only exit if not in testing mode
            print("CRITICAL ERROR: Pastikan semua file modul (data_handler, browser_automation, dll.) berada di dalam folder 'src/core_logic/'")
            print(f"Import error: {e}")
            exit()
        # In testing mode, create dummy imports to avoid SystemExit
        DataHandler = None
        Automation = None  
        FailedRowHandler = None
        parse_and_validate = None
        ExecutionMetricsTracker = None

def setup_logging_session() -> Path:
    """
    Membuat folder log unik untuk sesi ini dan mengkonfigurasi logger utama.
    Semua pesan log akan muncul di konsol DAN disimpan ke file.
    """
    session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_session_folder = Path("logs") / session_timestamp
    log_session_folder.mkdir(parents=True, exist_ok=True)
    
    log_file_path = log_session_folder / "run.log"
    
    # Konfigurasi logging. `StreamHandler` akan mencetak log ke konsol/terminal.
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)-8s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'), # Menyimpan ke file
            logging.StreamHandler()                               # Menampilkan di terminal
        ]
    )
    
    logging.info(f"Sesi logging dimulai. Log disimpan di: {log_session_folder}")
    return log_session_folder

def load_prompt(prompt_filepath: Path) -> str | None:
    """Membaca konten dari file prompt."""
    try:
        with open(prompt_filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"File prompt tidak ditemukan di: {prompt_filepath}", exc_info=True)
        return None

def main(args):
    """
    Main orchestrator function for auto-labeling process with metrics tracking.
    """
    session_log_path = setup_logging_session()
    
    # Initialize all main components before try block
    # so they can be accessed in finally block
    data_handler = None
    failed_handler = None
    browser = None
    metrics_tracker = None
    total_processed_rows = 0
    total_failed_rows = 0
    batch_count = 0
    allowed_labels_list = [label.strip().upper() for label in args.allowed_labels.split(',')]
    logging.info(f"Using allowed labels for validation: {allowed_labels_list}")

    try:
        # Initialize handlers
        data_handler = DataHandler(input_filepath=args.input_file)
        failed_handler = FailedRowHandler(log_folder=session_log_path, source_filename_stem=args.input_file.stem)
        browser = Automation(user_data_dir="browser_data", log_folder=session_log_path)
        
        # Initialize metrics tracker
        metrics_tracker = ExecutionMetricsTracker()
        total_rows = data_handler.get_unprocessed_data_count()
        
        if total_rows == 0:
            logging.info("No data to process. Finished.")
            return

        # Start metrics tracking session
        session_id = metrics_tracker.start_session(
            dataset_file=args.input_file,
            total_rows=total_rows,
            batch_size=args.batch_size
        )
        logging.info(f"📊 Started execution metrics tracking session: {session_id}")

        # Load data and prompt
        prompt_template = load_prompt(args.prompt_file)
        if not prompt_template: return

        try:
            # Move start_session into its own try block
            browser.start_session("https://aistudio.google.com/")
        except TimeoutError as e:
            # Catch specific error from start_session and end cleanly
            logging.critical(f"Failed to start browser session due to timeout. Stopping process. Details: {e}")
            # End metrics session with failure status
            if metrics_tracker:
                metrics_tracker.end_session("failed")
            return # Exit main function safely

        # Get and process batches
        batches = data_handler.get_data_batches(batch_size=args.batch_size)
        total_batches = len(batches)
        
        if args.debug:
            logging.warning("DEBUG MODE ACTIVE: Will only process 1 batch.")
            batches = batches[:1]

        for i, batch_data in enumerate(batches):
            logging.info(f"--- Processing Batch {i + 1}/{total_batches} (Size: {len(batch_data)} rows) ---")
            
            MAX_RETRIES = 3
            validated_results = None
            for attempt in range(MAX_RETRIES):
                logging.info(f"Attempt #{attempt + 1}/{MAX_RETRIES} for this batch...")
                
                full_prompt = f"{prompt_template}\n\n" + "\n".join(f'"{text}"' for text in batch_data)
                raw_response = browser.get_raw_response_for_batch(full_prompt)
                is_valid, result = parse_and_validate(
                    raw_response, 
                    expected_count=len(batch_data), 
                    allowed_labels=allowed_labels_list
                )

                # Save check data artifacts for each attempt
                check_data_path = session_log_path / f"check_data_batch_{i+1}_attempt_{attempt+1}.txt"
                with open(check_data_path, "w", encoding="utf-8") as f:
                    f.write(f"--- VALIDATION ---\nValid: {is_valid}\nResult/Error: {result}\n\n")
                    f.write(f"--- RAW RESPONSE ---\n{raw_response or 'NO RESPONSE EXTRACTED'}\n\n")
                    f.write(f"--- FULL PROMPT ---\n{full_prompt}\n\n")

                if is_valid:
                    logging.info(f"Batch #{i + 1} successfully validated on attempt #{attempt + 1}.")
                    validated_results = result
                    break # Exit retry loop if successful
                else:
                    logging.warning(f"Validation failed: {result}. Retrying in 5 seconds...")
                    browser.clear_chat_history()
                    time.sleep(5)

            # Save results or record failure
            if validated_results:
                data_handler.update_and_save_data(validated_results, start_index=total_processed_rows)
                total_processed_rows += len(validated_results)
                batch_count += 1
                logging.info(f"Progress saved. Total valid processed rows: {total_processed_rows}")
                
                # Update metrics progress
                if metrics_tracker:
                    metrics_tracker.update_progress(
                        processed_rows=total_processed_rows,
                        failed_rows=total_failed_rows,
                        batch_count=batch_count
                    )
            else:
                logging.error(f"Failed to process Batch #{i + 1} after {MAX_RETRIES} attempts. Recording rows as failed.")
                for text in batch_data:
                    failed_handler.add_failed_row(
                        original_text=text, invalid_label="N/A", justification="N/A",
                        reason=f"Failed validation after {MAX_RETRIES} attempts."
                    )
                    total_failed_rows += 1
                
                # Update metrics with failed rows
                if metrics_tracker:
                    metrics_tracker.update_progress(
                        processed_rows=total_processed_rows,
                        failed_rows=total_failed_rows,
                        batch_count=batch_count
                    )
    
    except KeyboardInterrupt:
        logging.warning("Process interrupted by user (Ctrl+C).")
        # End metrics session with interrupted status
        if metrics_tracker:
            final_metrics = metrics_tracker.end_session("interrupted")
            logging.info(f"📊 Final metrics - Duration: {final_metrics.get('duration_seconds', 0):.2f}s, Processed: {total_processed_rows} rows")
    except Exception as e:
        logging.critical(f"Fatal unhandled error occurred in main flow: {e}", exc_info=True)
        if browser and session_log_path:
            browser.page.screenshot(path=session_log_path / "FATAL_ERROR_screenshot.png")
        # End metrics session with failed status
        if metrics_tracker:
            metrics_tracker.end_session("failed")
    finally:
        # This block is ALWAYS executed, whether script succeeds, fails, or is interrupted.
        # This ensures safe cleanup.
        logging.info("--- Starting final cleanup process ---")
        if browser:
            browser.close_session()
        if failed_handler:
            failed_handler.save_to_file()
        if data_handler and total_processed_rows > 0:
            data_handler.save_final_results()
        
        # End metrics tracking session if still active
        if metrics_tracker and metrics_tracker.session_id:
            final_metrics = metrics_tracker.end_session("completed")
            if final_metrics:
                logging.info(f"📊 Execution completed - Duration: {final_metrics.get('duration_seconds', 0):.2f}s")
                logging.info(f"📊 Performance: {final_metrics.get('rows_per_second', 0):.2f} rows/second")
                logging.info(f"📊 Success rate: {final_metrics.get('success_rate', 0):.1f}%")
        
        logging.info("--- Auto-labeling process finished ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aplikasi Auto-Labeling menggunakan Aistudio.")
    parser.add_argument("--input-file", type=Path, required=True, help="Path ke file dataset (.csv atau .xlsx).")
    parser.add_argument("--prompt-file", type=Path, default=Path("prompts/prompt.txt"), help="Path ke file prompt teks.")
    parser.add_argument("--batch-size", type=int, default=50, help="Jumlah baris yang diproses per batch.")
    parser.add_argument("--debug", action="store_true", help="Jalankan dalam mode debug (hanya proses satu batch).")
    parser.add_argument(
        "--allowed-labels", 
        type=str, 
        default="POSITIF,NEGATIF,NETRAL,TIDAK RELEVAN", 
        help="Daftar label yang valid, dipisahkan koma."
    )
    
    args = parser.parse_args()
    
    main(args)