import logging
import os
import random
import time
from pathlib import Path
from typing import List, Tuple

from playwright.sync_api import sync_playwright

class Automation:
    """
    Menangani tugas otomatisasi browser untuk berinteraksi dengan Aistudio menggunakan Playwright.
    Menggunakan konteks browser persisten untuk mempertahankan sesi login.
    """
    def __init__(self, user_data_dir: str, log_folder: Path):
        """
        Menginisialisasi otomatisasi browser dengan mekanisme fallback.

        Args:
            user_data_dir (str): Path ke direktori untuk menyimpan data sesi browser.
            log_folder (Path): Path ke folder log sesi untuk menyimpan screenshot & file debug.
        """
        self.log_folder = log_folder
        self.playwright = sync_playwright().start()
        self.context = None
        self.browser = None
        self.page = None
        
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        
        os.makedirs(user_data_dir, exist_ok=True)
        
        # Coba beberapa strategi untuk meluncurkan browser
        success = False
        
        # STRATEGI 1: Launch persistent context (preferred)
        try:
            logging.info("Meluncurkan browser Chromium dengan konteks persisten...")
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                channel="chrome",
                slow_mo=150,
                user_agent=user_agent,
                viewport={"width": 1280, "height": 800},
                args=[
                    '--no-sandbox',
                    '--start-maximized',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials'
                ]
            )
            
            if self.context.pages:
                self.page = self.context.pages[0]
            else:
                self.page = self.context.new_page()
            
            success = True
            logging.info("✅ Berhasil meluncurkan browser dengan persistent context.")
            
        except Exception as e:
            logging.warning(f"❌ Gagal meluncurkan persistent context: {e}")
            
            # STRATEGI 2: Launch regular browser tanpa persistent context
            try:
                logging.info("Mencoba meluncurkan browser reguler...")
                self.browser = self.playwright.chromium.launch(
                    headless=False,
                    channel="chrome",
                    slow_mo=150,
                    args=[
                        '--no-sandbox',
                        '--start-maximized',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--disable-site-isolation-trials'
                    ]
                )
                
                self.context = self.browser.new_context(
                    user_agent=user_agent,
                    viewport={"width": 1280, "height": 800}
                )
                
                self.page = self.context.new_page()
                success = True
                logging.info("✅ Berhasil meluncurkan browser reguler.")
                
            except Exception as e2:
                logging.error(f"❌ Gagal meluncurkan browser reguler: {e2}")
                
                # STRATEGI 3: Launch headless sebagai fallback terakhir
                try:
                    logging.info("Mencoba meluncurkan browser headless sebagai fallback...")
                    self.browser = self.playwright.chromium.launch(
                        headless=True,
                        args=['--no-sandbox']
                    )
                    
                    self.context = self.browser.new_context(
                        user_agent=user_agent,
                        viewport={"width": 1280, "height": 800}
                    )
                    
                    self.page = self.context.new_page()
                    success = True
                    logging.warning("⚠️ Berhasil meluncurkan browser headless (tidak ada UI).")
                    
                except Exception as e3:
                    logging.critical(f"❌ Gagal meluncurkan browser sama sekali: {e3}")
        
        if not success or not self.page:
            logging.critical("============================================================")
            logging.critical("GAGAL TOTAL MELUNCURKAN BROWSER!")
            logging.critical(f"Detail Error: {e}")
            logging.critical("")
            logging.critical("Ini kemungkinan besar adalah masalah lingkungan, bukan kode.")
            logging.critical("SOLUSI YANG DISARANKAN:")
            logging.critical("1. Tutup semua jendela Google Chrome yang terbuka.")
            logging.critical("2. Buka terminal/CMD, aktifkan venv, dan jalankan perintah berikut:")
            logging.critical("   playwright uninstall")
            logging.critical("   playwright install")
            logging.critical("3. Coba jalankan kembali aplikasi.")
            logging.critical("============================================================")
            raise RuntimeError("Gagal meluncurkan browser setelah mencoba semua metode fallback.") from e
        
        # Set timeout default
        try:
            self.page.set_default_timeout(60000)  # Timeout default 60 detik
        except Exception as e:
            logging.warning(f"Gagal mengatur timeout default: {e}")
        

    def _apply_stealth_techniques(self):
        """Menerapkan teknik untuk membuat browser tampak lebih manusiawi."""
        js_script = """
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        window.chrome = { runtime: {} };
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        """
        try:
            self.page.evaluate(js_script)
            logging.info("Berhasil menerapkan penyamaran anti-deteksi pada browser.")
        except Exception as e:
            logging.warning(f"Tidak dapat menerapkan teknik penyamaran: {e}", exc_info=True)

    def start_session(self, url: str):
        """
        Menavigasi ke URL yang ditentukan dan menunggu UI utama siap.
        """
        logging.info(f"Memastikan browser berada di URL: {url}...")
        self._apply_stealth_techniques()
        
        if "aistudio.google.com" not in self.page.url:
            logging.info(f"Menavigasi ke {url}...")
            self.page.goto(url, wait_until="domcontentloaded", timeout=90000)

        logging.info("Halaman dimuat. Menunggu Aistudio siap...")
        try:
            input_locator = self.page.locator('ms-chunk-input textarea')
            input_locator.wait_for(state="visible", timeout=180000) # Tunggu hingga 3 menit
            
            # Ambil screenshot tampilan awal untuk debugging
            self.page.screenshot(path=self.log_folder / "debug_session_start.png")
            logging.info("Aistudio siap. Kotak input utama terdeteksi.")

        except Exception as e:
            logging.critical("="*50)
            logging.critical("MASALAH TIMEOUT ATAU LOGIN TERDETEKSI")
            logging.critical("Skrip tidak dapat menemukan kotak input utama setelah 3 menit.")
            logging.critical("Pastikan Anda sudah login dan tidak ada pop-up yang menghalangi.")
            logging.critical(f"Detail Error: {e}", exc_info=True)
            
            try:
                self.page.screenshot(path=self.log_folder / "FATAL_ERROR_timeout.png")
            except Exception as screenshot_error:
                logging.error(f"Gagal mengambil screenshot error: {screenshot_error}")
            
            raise TimeoutError("Gagal memulai sesi: Timeout saat menunggu elemen login.") from e

    def get_raw_response_for_batch(self, full_prompt: str) -> str | None:
        """
        Mengirimkan satu batch data ke Aistudio dan mengembalikan respons teks mentah.
        Memiliki logika retry internal untuk mengatasi error UI atau API sementara.

        Args:
            full_prompt (str): Prompt lengkap, termasuk data batch.

        Returns:
            str | None: Teks respons mentah jika berhasil, atau None jika semua percobaan gagal.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = 5 * attempt
                    logging.warning(f"Percobaan ke-{attempt + 1}/{max_retries}. Menunggu {delay} detik sebelum mencoba lagi...")
                    time.sleep(delay)
                    logging.info("Memuat ulang halaman sebelum mencoba lagi...")
                    self.page.reload(wait_until="domcontentloaded")
                    self.page.wait_for_selector('ms-chunk-input textarea', timeout=60000)

                logging.info(f"Memproses batch, percobaan #{attempt + 1}...")
                
                input_textbox_selector = 'ms-chunk-input textarea'
                send_button_selector = 'footer button[aria-label="Run"]'
                
                # Mengisi prompt
                self.page.fill(input_textbox_selector, full_prompt)
                
                # Mengklik tombol kirim
                self.page.click(send_button_selector)
                logging.info("Prompt dikirim. Menunggu respons dari model...")

                self.page.screenshot(path=self.log_folder / f"debug_before_response_gen_attempt_{attempt+1}.png")

                # Logika penungguan dinamis
                if not self._wait_for_generation_to_complete():
                    logging.error("Model tidak menyelesaikan generasi dalam waktu yang ditentukan.")
                    continue # Lanjut ke percobaan berikutnya

                self.page.screenshot(path=self.log_folder / f"debug_after_response_gen_attempt_{attempt+1}.png")
                time.sleep(2) # Beri waktu ekstra untuk UI render

                # Logika ekstraksi respons berlapis
                raw_response = self._extract_response_text()

                if raw_response and "internal error" not in raw_response.lower():
                    logging.info(f"Berhasil mengekstrak respons dari model (panjang: {len(raw_response)} karakter).")
                    return raw_response
                elif raw_response:
                    logging.warning(f"Respons berisi pesan error: '{raw_response[:100]}...'. Mencoba lagi...")
                    continue
                else:
                    logging.warning("Gagal mengekstrak respons pada percobaan ini. Mencoba lagi...")
                    continue

            except Exception as e:
                logging.error(f"Terjadi error saat memproses batch pada percobaan #{attempt + 1}: {e}", exc_info=True)
                try:
                    self.page.screenshot(path=self.log_folder / f"ERROR_process_batch_attempt_{attempt+1}.png")
                except Exception as screenshot_error:
                    logging.error(f"Gagal mengambil screenshot error: {screenshot_error}")
        
        logging.error(f"Gagal memproses batch setelah {max_retries} percobaan.")
        return None

    def _wait_for_generation_to_complete(self) -> bool:
        """
        Logika penungguan dinamis untuk mendeteksi kapan respons AI selesai dibuat.
        """
        logging.info("Memulai logika penungguan dinamis...")
        max_wait_time = 240  # Maksimal 4 menit
        start_wait_time = time.time()
        
        # Tunggu hingga tombol 'Stop' muncul (menandakan generasi dimulai)
        try:
            self.page.locator('button:has-text("Stop")').wait_for(state="visible", timeout=30000)
            logging.info("Generasi dimulai (tombol 'Stop' terdeteksi).")
        except Exception:
            logging.warning("Tidak mendeteksi tombol 'Stop', mungkin generasi gagal dimulai atau sudah selesai.")
            # Tetap lanjutkan, mungkin respons muncul sangat cepat.

        while True:
            elapsed = time.time() - start_wait_time
            if elapsed > max_wait_time:
                logging.error(f"Waktu tunggu maksimum ({max_wait_time} detik) terlampaui.")
                return False

            # Indikator utama: Tombol 'Stop' menghilang
            try:
                if self.page.locator('button:has-text("Stop")').count() == 0:
                    logging.info(f"Generasi selesai (tombol 'Stop' menghilang) setelah {elapsed:.1f} detik.")
                    return True
            except Exception:
                # Jika ada error saat mengecek locator, anggap saja masih ada
                pass
            
            # Beri jeda singkat antar pengecekan
            time.sleep(2)

    def _extract_response_text(self) -> str | None:
        """
        Mengekstrak teks respons dengan menemukan baris valid pertama dan
        mengambil semua konten dari titik itu hingga akhir.
        """
        logging.info("Memulai ekstraksi respons dengan metode 'Temukan Awal dan Ambil Sisanya'...")

        # JavaScript function yang akan kita inject.
        js_extractor_function = """
        (element) => {
            const text = element.innerText;
            if (!text) return null;

            const lines = text.split('\\n');
            
            // Pola Regex untuk memeriksa baris pertama yang valid.
            const validStartLineRegex = /^(POSITIF|NEGATIF|NETRAL|TIDAK RELEVAN)\\s*-\\s*.+/i;

            // Cari indeks dari baris valid pertama
            let startIndex = -1;
            for (let i = 0; i < lines.length; i++) {
                if (validStartLineRegex.test(lines[i].trim())) {
                    startIndex = i;
                    break; // Hentikan pencarian setelah menemukan yang pertama
                }
            }

            // Jika baris valid ditemukan...
            if (startIndex !== -1) {
                // ...ambil semua baris dari indeks itu hingga akhir...
                const relevantLines = lines.slice(startIndex);
                // ...dan gabungkan kembali menjadi satu blok teks.
                return relevantLines.join('\\n');
            }
            
            // Jika tidak ada baris valid yang ditemukan sama sekali
            return null;
        }
        """

        # --- STRATEGI 1: Cari di dalam kontainer yang paling mungkin ---
        potential_container_selectors = [
            'ms-message-content:last-of-type',
            'div.model-response-text:last-of-type'
        ]

        for selector in potential_container_selectors:
            logging.info(f"Mencoba mengekstrak dari kontainer: '{selector}'")
            try:
                container_handle = self.page.query_selector(selector)
                if container_handle:
                    # Jalankan fungsi JavaScript PADA elemen kontainer yang ditemukan
                    extracted_text = container_handle.evaluate(js_extractor_function)
                    
                    if extracted_text and extracted_text.strip():
                        logging.info(f"✅ Ekstraksi berhasil dari '{selector}'.")
                        return extracted_text
                else:
                    logging.info(f"Kontainer '{selector}' tidak ditemukan.")
            except Exception as e:
                logging.error(f"Error saat mengekstrak dari '{selector}': {e}")
                continue

        # --- STRATEGI 2: Jika kontainer tidak ditemukan, cari di seluruh body (CADANGAN) ---
        logging.warning("Tidak berhasil mengekstrak dari kontainer spesifik. Mencoba di seluruh body dokumen...")
        try:
            body_handle = self.page.query_selector('body')
            if body_handle:
                extracted_text = body_handle.evaluate(js_extractor_function)
                
                if extracted_text and extracted_text.strip():
                    logging.info("✅ Ekstraksi cadangan berhasil dari <body>.")
                    return extracted_text
        except Exception as e:
            logging.error(f"Ekstraksi cadangan dari <body> gagal: {e}", exc_info=True)

        logging.error("Semua metode ekstraksi gagal menemukan baris respons yang valid.")
        try:
            self.page.screenshot(path=self.log_folder / "ERROR_extraction_failed.png")
        except Exception as screenshot_error:
            logging.error(f"Gagal mengambil screenshot error ekstraksi: {screenshot_error}")
        return None

    def clear_chat_history(self):
        """Membersihkan riwayat obrolan dengan memulai obrolan baru."""
        try:
            logging.info("Membersihkan riwayat obrolan...")
            self.page.locator('a.nav-item:has-text("Chat")').click()
            self.page.locator('ms-chunk-input textarea').wait_for(state="visible", timeout=60000)
            time.sleep(2)
            logging.info("Riwayat obrolan dibersihkan.")
        except Exception as e:
            logging.warning(f"Tidak dapat membersihkan riwayat, memuat ulang halaman sebagai alternatif: {e}")
            self.page.reload(wait_until="domcontentloaded")
            self.page.locator('ms-chunk-input textarea').wait_for(state="visible", timeout=60000)

    def close_session(self):
        """Menutup sesi browser dengan aman."""
        logging.info("Menutup sesi browser.")
        try:
            if hasattr(self, 'context') and self.context:
                self.context.close()
            if hasattr(self, 'browser') and self.browser:
                self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
        except Exception as e:
            logging.warning(f"Error saat menutup browser: {e}")
            # Paksa tutup playwright jika masih ada
            try:
                if hasattr(self, 'playwright') and self.playwright:
                    self.playwright.stop()
            except:
                pass