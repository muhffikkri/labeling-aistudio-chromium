import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import pandas as pd

class DataHandler:
    def __init__(self, input_filepath: Path):
        """
        Menginisialisasi DataHandler dengan path ke file dataset.

        Args:
            input_filepath (Path): Path ke file .xlsx atau .csv.
        """
        self.input_filepath = input_filepath
        
        # Membuat nama file output yang unik di folder 'results'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{input_filepath.stem}_labeled_{timestamp}{input_filepath.suffix}"
        
        # Pastikan folder results ada
        Path("results").mkdir(exist_ok=True)
        self.output_filepath = Path("results") / output_filename
        
        logging.info(f"File input: {self.input_filepath}")
        logging.info(f"File output akan disimpan di: {self.output_filepath}")

        try:
            if not self.input_filepath.is_file():
                raise FileNotFoundError(f"File input tidak ditemukan di: {self.input_filepath}")

            if self.input_filepath.suffix == '.xlsx':
                self.df = pd.read_excel(self.input_filepath)
                logging.info(f"Berhasil membaca file Excel dengan {len(self.df)} baris.")
            elif self.input_filepath.suffix == '.csv':
                self.df = pd.read_csv(self.input_filepath)
                logging.info(f"Berhasil membaca file CSV dengan {len(self.df)} baris.")
            else:
                raise ValueError("Format file tidak didukung. Harap gunakan .xlsx atau .csv")
                
        except Exception as e:
            logging.critical(f"Gagal memuat atau membaca file data: {e}", exc_info=True)
            # Buat DataFrame kosong agar aplikasi tidak crash, tetapi tidak akan ada yang diproses.
            self.df = pd.DataFrame(columns=['full_text', 'label', 'justification'])
            # Hentikan eksekusi jika file data tidak bisa dimuat
            raise e

        # Memastikan kolom yang diperlukan ada
        self._ensure_columns_exist()

    def _ensure_columns_exist(self):
        """Memastikan kolom 'label' dan 'justification' ada di DataFrame."""
        made_changes = False
        if 'label' not in self.df.columns:
            logging.warning("Kolom 'label' tidak ditemukan. Membuat kolom baru.")
            self.df['label'] = np.nan
            made_changes = True
            
        if 'justification' not in self.df.columns:
            logging.warning("Kolom 'justification' tidak ditemukan. Membuat kolom baru.")
            self.df['justification'] = np.nan
            made_changes = True

        if made_changes:
            # Segera simpan perubahan struktur kembali ke file input
            self.save_progress()

    def get_data_batches(self, batch_size: int = 50) -> List[List[str]]:
        """
        Memecah kolom 'full_text' dari baris yang belum diproses menjadi beberapa batch.

        Args:
            batch_size (int): Jumlah item per batch.

        Returns:
            List[List[str]]: Daftar batch, di mana setiap batch adalah daftar teks.
        """
        if 'full_text' not in self.df.columns:
            logging.error("Kolom 'full_text' tidak ditemukan di dataset.")
            return []
        
        unprocessed_df = self.df[self.df['label'].isnull()]
        texts = unprocessed_df['full_text'].tolist()
        logging.info(f"Membagi {len(texts)} baris yang belum diproses menjadi batch berukuran {batch_size}.")
        return [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]

    def update_and_save_data(self, results: List[Dict[str, Any]], start_index: int):
        """
        Memperbarui DataFrame dengan label dan justifikasi, lalu menyimpan progres.

        Args:
            results (List[Dict[str, Any]]): Daftar dict, masing-masing berisi {"label": ..., "justification": ...}.
            start_index (int): Indeks awal absolut dari data yang belum diproses untuk diperbarui.
        """
        # Dapatkan indeks dari semua baris yang belum diproses
        unprocessed_indices = self.df[self.df['label'].isnull()].index
        
        # Tentukan slice dari indeks yang akan diperbarui
        indices_to_update = unprocessed_indices[start_index : start_index + len(results)]

        for i, result_dict in enumerate(results):
            if i < len(indices_to_update):
                actual_index = indices_to_update[i]
                self.df.loc[actual_index, 'label'] = result_dict["label"]
                self.df.loc[actual_index, 'justification'] = result_dict["justification"]

        self.save_progress()

    def save_progress(self):
        """Menyimpan progres saat ini kembali ke file INPUT asli."""
        try:
            if self.input_filepath.suffix == '.xlsx':
                self.df.to_excel(self.input_filepath, index=False)
            elif self.input_filepath.suffix == '.csv':
                self.df.to_csv(self.input_filepath, index=False)
            logging.info(f"Progres disimpan ke {self.input_filepath}")
        except Exception as e:
            logging.error(f"Gagal menyimpan progres ke file input: {e}", exc_info=True)

    def save_final_results(self):
        """Menyimpan DataFrame lengkap ke file OUTPUT di folder results."""
        try:
            if self.output_filepath.suffix == '.xlsx':
                self.df.to_excel(self.output_filepath, index=False)
            elif self.output_filepath.suffix == '.csv':
                self.df.to_csv(self.output_filepath, index=False)
            logging.info(f"Hasil akhir yang bersih disimpan ke {self.output_filepath}")
        except Exception as e:
            logging.error(f"Gagal menyimpan hasil akhir: {e}", exc_info=True)

    def get_unprocessed_data_count(self) -> int:
        """Menghitung jumlah baris yang belum memiliki label."""
        if 'label' not in self.df.columns:
            return 0
        
        # Menganggap baris belum diproses jika labelnya null/NaN.
        unprocessed_count = self.df['label'].isnull().sum()
        return unprocessed_count