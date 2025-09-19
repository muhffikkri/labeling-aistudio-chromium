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
except ImportError:
    print("CRITICAL ERROR: Pastikan semua file modul (data_handler, browser_automation, dll.) berada di dalam folder 'src/core_logic/'")
    exit()

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
    Fungsi orkestrator utama untuk proses auto-labeling.
    """
    session_log_path = setup_logging_session()
    
    # Inisialisasi semua komponen utama sebelum blok try
    # agar bisa diakses di blok finally
    data_handler = None
    failed_handler = None
    browser = None
    total_processed_rows = 0
    allowed_labels_list = [label.strip().upper() for label in args.allowed_labels.split(',')]
    logging.info(f"Menggunakan label yang diizinkan untuk validasi: {allowed_labels_list}")

    try:
        # Inisialisasi handler
        data_handler = DataHandler(input_filepath=args.input_file)
        failed_handler = FailedRowHandler(log_folder=session_log_path, source_filename_stem=args.input_file.stem)
        browser = Automation(user_data_dir="browser_data", log_folder=session_log_path)

        # Muat data dan prompt
        prompt_template = load_prompt(args.prompt_file)
        if not prompt_template: return

        if data_handler.get_unprocessed_data_count() == 0:
            logging.info("Tidak ada data yang perlu diproses. Selesai.")
            return

        try:
            # Pindahkan start_session ke dalam blok try-nya sendiri
            browser.start_session("https://aistudio.google.com/")
        except TimeoutError as e:
            # Tangkap error spesifik dari start_session dan akhiri dengan bersih
            logging.critical(f"Gagal memulai sesi browser karena timeout. Menghentikan proses. Detail: {e}")
            # Tidak perlu melakukan apa-apa lagi, blok finally akan membereskannya.
            return # Keluar dari fungsi main dengan aman

        # Dapatkan dan proses batch
        batches = data_handler.get_data_batches(batch_size=args.batch_size)
        total_batches = len(batches)
        
        if args.debug:
            logging.warning("MODE DEBUG AKTIF: Hanya akan memproses 1 batch.")
            batches = batches[:1]

        for i, batch_data in enumerate(batches):
            logging.info(f"--- Memproses Batch {i + 1}/{total_batches} (Ukuran: {len(batch_data)} baris) ---")
            
            MAX_RETRIES = 3
            validated_results = None
            for attempt in range(MAX_RETRIES):
                logging.info(f"Percobaan #{attempt + 1}/{MAX_RETRIES} untuk batch ini...")
                
                full_prompt = f"{prompt_template}\n\n" + "\n".join(f'"{text}"' for text in batch_data)
                raw_response = browser.get_raw_response_for_batch(full_prompt)
                is_valid, result = parse_and_validate(
                    raw_response, 
                    expected_count=len(batch_data), 
                    allowed_labels=allowed_labels_list
                )

                # Simpan artefak pengecekan data untuk setiap percobaan
                check_data_path = session_log_path / f"check_data_batch_{i+1}_attempt_{attempt+1}.txt"
                with open(check_data_path, "w", encoding="utf-8") as f:
                    f.write(f"--- VALIDATION ---\nValid: {is_valid}\nResult/Error: {result}\n\n")
                    f.write(f"--- RAW RESPONSE ---\n{raw_response or 'NO RESPONSE EXTRACTED'}\n\n")

                if is_valid:
                    logging.info(f"Batch #{i + 1} berhasil divalidasi pada percobaan #{attempt + 1}.")
                    validated_results = result
                    break # Keluar dari loop retry jika berhasil
                else:
                    logging.warning(f"Validasi gagal: {result}. Mencoba lagi dalam 5 detik...")
                    browser.clear_chat_history()
                    time.sleep(5)

            # Simpan hasil atau catat kegagalan
            if validated_results:
                data_handler.update_and_save_data(validated_results, start_index=total_processed_rows)
                total_processed_rows += len(validated_results)
                logging.info(f"Progres disimpan. Total baris terproses yang valid: {total_processed_rows}")
            else:
                logging.error(f"Gagal memproses Batch #{i + 1} setelah {MAX_RETRIES} percobaan. Mencatat baris sebagai gagal.")
                for text in batch_data:
                    failed_handler.add_failed_row(
                        original_text=text, invalid_label="N/A", justification="N/A",
                        reason=f"Gagal divalidasi setelah {MAX_RETRIES} percobaan."
                    )
    
    except KeyboardInterrupt:
        logging.warning("Proses dihentikan oleh pengguna (Ctrl+C).")
    except Exception as e:
        logging.critical(f"Terjadi error fatal yang tidak tertangani di alur utama: {e}", exc_info=True)
        if browser and session_log_path:
            browser.page.screenshot(path=session_log_path / "FATAL_ERROR_screenshot.png")
    finally:
        # Blok ini SELALU dijalankan, baik skrip berhasil, gagal, atau dihentikan.
        # Ini memastikan cleanup yang aman.
        logging.info("--- Memulai proses cleanup akhir ---")
        if browser:
            browser.close_session()
        if failed_handler:
            failed_handler.save_to_file()
        if data_handler and total_processed_rows > 0:
            data_handler.save_final_results()
        logging.info("--- Proses auto-labeling selesai ---")

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