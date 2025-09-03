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
        Menginisialisasi otomatisasi browser.

        Args:
            user_data_dir (str): Path ke direktori untuk menyimpan data sesi browser.
            log_folder (Path): Path ke folder log sesi untuk menyimpan screenshot & file debug.
        """
        self.log_folder = log_folder
        self.playwright = sync_playwright().start()
        
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        
        os.makedirs(user_data_dir, exist_ok=True)
        
        logging.info("Meluncurkan browser Chromium dengan konteks persisten...")
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            channel="chrome",
            slow_mo=150,
            user_agent=user_agent,
            viewport={"width": 1280, "height": 800},
            args=[
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
        
        self.page.set_default_timeout(60000) # Timeout default 60 detik

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
            self.page.screenshot(path=self.log_folder / "FATAL_ERROR_timeout.png")
            self.close_session()
            exit()

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
                    logging.info("Berhasil mengekstrak respons dari model.")
                    return raw_response
                elif raw_response:
                    logging.warning(f"Respons berisi pesan error: '{raw_response[:100]}...'. Mencoba lagi...")
                    continue
                else:
                    logging.warning("Gagal mengekstrak respons pada percobaan ini. Mencoba lagi...")
                    continue

            except Exception as e:
                logging.error(f"Terjadi error saat memproses batch pada percobaan #{attempt + 1}: {e}", exc_info=True)
                self.page.screenshot(path=self.log_folder / f"ERROR_process_batch_attempt_{attempt+1}.png")
        
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
        Mencoba mengekstrak teks respons menggunakan beberapa metode.
        """
        logging.info("Memulai ekstraksi respons berlapis...")
        
        # Metode 1: Selector CSS Primer
        selectors = ['div.model-response-text', 'div.response-content', 'ms-message div.content']
        for selector in selectors:
            try:
                if self.page.locator(selector).count() > 0:
                    # Ambil teks dari elemen terakhir, karena UI bisa streaming
                    response = self.page.locator(selector).last.inner_text()
                    if response.strip():
                        logging.info(f"Ekstraksi berhasil menggunakan selector: '{selector}'")
                        return response
            except Exception:
                continue
        
        # Metode 2: Evaluasi JavaScript
        try:
            response = self.page.evaluate("""() => {
                const elements = Array.from(document.querySelectorAll('*'));
                const elementsWithLabels = elements.filter(el => {
                    const text = el.textContent || '';
                    return (text.includes('POSITIF') || text.includes('NEGATIF') || text.includes('NETRAL')) && el.offsetParent;
                });
                if (elementsWithLabels.length > 0) {
                    elementsWithLabels.sort((a, b) => b.textContent.length - a.textContent.length);
                    return elementsWithLabels[0].textContent;
                }
                return null;
            }""")
            if response and response.strip():
                logging.info("Ekstraksi berhasil menggunakan evaluasi JavaScript.")
                return response
        except Exception as e:
            logging.warning(f"Ekstraksi JavaScript gagal: {e}")

        logging.error("Semua metode ekstraksi gagal menemukan teks respons.")
        self.page.screenshot(path=self.log_folder / "ERROR_extraction_failed.png")
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
        if hasattr(self, 'context') and self.context:
            self.context.close()
        if hasattr(self, 'playwright') and self.playwright:
            self.playwright.stop()