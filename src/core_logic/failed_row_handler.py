import logging
from pathlib import Path
from typing import List

import pandas as pd

class FailedRowHandler:
    def __init__(self, log_folder: Path, source_filename_stem: str):
        """
        Menginisialisasi handler untuk baris-baris yang gagal divalidasi.
        File output akan disimpan di dalam folder log sesi.

        Args:
            log_folder (Path): Path ke folder log sesi yang unik.
            source_filename_stem (str): Nama file asli tanpa ekstensi, untuk penamaan file output.
        """
        # Membuat path file output yang dinamis di dalam folder log sesi
        self.file_path = log_folder / f"failed_rows_for_{source_filename_stem}.xlsx"
        self.failed_rows: List[dict] = []
        logging.info(f"FailedRowHandler diinisialisasi. Kegagalan akan disimpan di: {self.file_path}")

    def add_failed_row(self, original_text: str, invalid_label: str, justification: str, reason: str):
        """
        Menambahkan baris yang gagal ke daftar internal untuk disimpan nanti.
        
        Args:
            original_text (str): Teks 'full_text' asli yang diproses.
            invalid_label (str): Label tidak valid yang diterima dari AI (jika ada).
            justification (str): Justifikasi yang diterima (jika ada).
            reason (str): Alasan kegagalan (misalnya, "Validasi Gagal").
        """
        self.failed_rows.append({
            "full_text": original_text,
            "invalid_label": invalid_label,
            "justification": justification,
            "failure_reason": reason
        })
        logging.warning(f"Mencatat baris gagal. Alasan: {reason}. Teks: '{original_text[:50]}...'")

    def save_to_file(self):
        """
        Menyimpan semua baris gagal yang terkumpul ke file Excel.
        Akan menimpa file jika sudah ada, karena ini spesifik untuk satu sesi.
        """
        if not self.failed_rows:
            logging.info("Tidak ada baris gagal untuk disimpan.")
            return

        new_failures_df = pd.DataFrame(self.failed_rows)

        try:
            # Karena file ini spesifik per sesi, kita tidak perlu menggabungkan (append),
            # cukup tulis saja.
            logging.info(f"Menyimpan {len(new_failures_df)} baris gagal ke: {self.file_path}")
            new_failures_df.to_excel(self.file_path, index=False)
            logging.info("File baris gagal berhasil disimpan.")
            
            # Kosongkan daftar setelah disimpan
            self.failed_rows = []
        except Exception as e:
            logging.error(f"Terjadi error saat menyimpan file baris gagal: {e}", exc_info=True)