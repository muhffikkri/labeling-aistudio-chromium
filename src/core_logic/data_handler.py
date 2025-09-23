import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import pandas as pd

class DataHandler:
    def __init__(self, input_filepath: Path, output_dir: Path = None):
        """
        Menginisialisasi DataHandler dengan path ke file dataset.

        Args:
            input_filepath (Path): Path ke file .xlsx atau .csv.
            output_dir (Path, optional): Direktori khusus untuk output. Jika None, gunakan folder 'results'.
        """
        self.input_filepath = input_filepath
        
        # Membuat nama file output yang unik
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{input_filepath.stem}_labeled_{timestamp}{input_filepath.suffix}"
        
        # Tentukan direktori output
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path("results")
        
        # Pastikan folder output ada
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_filepath = self.output_dir / output_filename
        
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
        
        # Cek dan merge existing progress setelah load input file
        self._check_and_merge_existing_progress()
        
    def _check_and_merge_existing_progress(self):
        """
        Cek apakah ada file progress sebelumnya yang bisa dilanjutkan.
        Jika ada, merge progress tersebut dengan data input saat ini.
        """
        base_pattern = f"{self.input_filepath.stem}_labeled_*{self.input_filepath.suffix}"
        existing_files = list(self.output_dir.glob(base_pattern))
        
        # Sort berdasarkan waktu modifikasi (terbaru dulu)
        existing_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if existing_files:
            latest_file = existing_files[0]
            logging.info(f"🔄 Ditemukan file progress: {latest_file.name}")
            
            try:
                # Load existing progress file
                if latest_file.suffix == '.xlsx':
                    existing_df = pd.read_excel(latest_file)
                else:
                    existing_df = pd.read_csv(latest_file)
                
                # Cek apakah ada progress yang valid dan struktur cocok
                if ('label' in existing_df.columns and 
                    len(existing_df) == len(self.df) and
                    'full_text' in existing_df.columns):
                    
                    processed_count = existing_df['label'].notnull().sum()
                    if processed_count > 0:
                        logging.info(f"📊 File progress memiliki {processed_count} baris yang sudah diproses")
                        logging.info(f"🔄 Merging progress dari: {latest_file.name}")
                        
                        # Merge label dan justification yang sudah ada
                        for idx in existing_df.index:
                            if pd.notnull(existing_df.loc[idx, 'label']):
                                self.df.loc[idx, 'label'] = existing_df.loc[idx, 'label']
                                if 'justification' in existing_df.columns and pd.notnull(existing_df.loc[idx, 'justification']):
                                    self.df.loc[idx, 'justification'] = existing_df.loc[idx, 'justification']
                        
                        # Gunakan file yang sudah ada sebagai output
                        self.output_filepath = latest_file
                        logging.info(f"✅ Berhasil merge progress dari file yang ada")
                        return
                        
            except Exception as e:
                logging.warning(f"⚠️ Tidak bisa merge file progress: {e}. Buat file baru.")

    def get_progress_info(self) -> Dict[str, Any]:
        """
        Mendapatkan informasi progress lengkap.
        
        Returns:
            Dict dengan informasi total, processed, unprocessed, dan percentage.
        """
        total = len(self.df)
        processed = self.get_processed_data_count()
        unprocessed = self.get_unprocessed_data_count()
        percentage = (processed / total * 100) if total > 0 else 0
        
        return {
            'total_rows': total,
            'processed_rows': processed,
            'unprocessed_rows': unprocessed,
            'progress_percentage': round(percentage, 2)
        }

    def _ensure_columns_exist(self):
        """Memastikan kolom 'label' dan 'justification' ada di DataFrame."""
        made_changes = False
        if 'label' not in self.df.columns:
            logging.warning("Kolom 'label' tidak ditemukan. Membuat kolom baru.")
            self.df['label'] = pd.Series(dtype=object)  # Explicit object type
            made_changes = True
            
        if 'justification' not in self.df.columns:
            logging.warning("Kolom 'justification' tidak ditemukan. Membuat kolom baru.")
            self.df['justification'] = pd.Series(dtype=object)  # Explicit object type
            made_changes = True

        # Ensure columns are object type to avoid pandas warnings
        if self.df['label'].dtype != 'object':
            self.df['label'] = self.df['label'].astype(object)
        if self.df['justification'].dtype != 'object':
            self.df['justification'] = self.df['justification'].astype(object)

        if made_changes:
            logging.info("Struktur kolom telah disesuaikan - perubahan akan disimpan ke file hasil akhir")
            # Tidak lagi menyimpan perubahan struktur kembali ke file input
            # Data akan disimpan hanya ke file hasil akhir

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
        Memperbarui DataFrame dengan label dan justifikasi tanpa menyimpan ke file input.
        Data hanya akan disimpan ke file hasil akhir saja.

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

        logging.info(f"Data batch berhasil diperbarui dalam memori (tidak menyimpan ke file input)")
        
    def save_incremental_progress(self):
        """
        Menyimpan progress saat ini secara incremental ke file output.
        Dipanggil setelah setiap batch berhasil diproses untuk memastikan
        tidak ada data yang hilang jika terjadi error atau interruption.
        """
        try:
            if self.output_filepath.suffix == '.xlsx':
                self.df.to_excel(self.output_filepath, index=False)
            elif self.output_filepath.suffix == '.csv':
                self.df.to_csv(self.output_filepath, index=False)
            
            processed_count = self.get_processed_data_count()
            unprocessed_count = self.get_unprocessed_data_count()
            
            logging.info(f"✅ Progress disimpan incremental ke {self.output_filepath.name} - "
                        f"Diproses: {processed_count}, Tersisa: {unprocessed_count}")
            
        except Exception as e:
            logging.error(f"❌ Gagal menyimpan progress incremental: {e}", exc_info=True)
            # Jangan raise exception agar proses bisa dilanjutkan
    
    def get_processed_data_count(self) -> int:
        """Menghitung jumlah baris yang sudah memiliki label."""
        if 'label' not in self.df.columns:
            return 0
        
        processed_count = self.df['label'].notnull().sum()
        return processed_count

    def save_progress(self):
        """
        DEPRECATED: Fungsi ini tidak lagi digunakan untuk menghindari modifikasi file input.
        Data progress sekarang hanya disimpan ke file hasil akhir melalui save_final_results().
        """
        logging.warning("save_progress() dipanggil tetapi diabaikan - data hanya akan disimpan ke file hasil akhir")
        pass

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