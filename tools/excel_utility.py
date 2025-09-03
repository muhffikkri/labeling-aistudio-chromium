import argparse
import logging
import os
import shutil
import sys
import time
from pathlib import Path

import pandas as pd

# Menambahkan blok try-except untuk impor agar memberikan pesan error yang lebih baik
# jika struktur folder tidak benar.
try:
    from src.core_logic.data_handler import DataHandler
except ImportError:
    print("FATAL ERROR: Tidak dapat mengimpor DataHandler. Pastikan Anda menjalankan skrip ini sebagai modul dari direktori root proyek.")
    print("Contoh: python -m tools.excel_utility diagnose ...")
    sys.exit(1)

# Konfigurasi logging dasar untuk alat bantu CLI.
# Pesan akan dicetak langsung ke konsol.
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def is_file_locked(filepath: str) -> bool:
    """Memeriksa apakah file terkunci dengan mencoba membukanya dalam mode tulis."""
    if not os.path.exists(filepath):
        return False
        
    try:
        # Menggunakan 'a+b' (append binary) adalah cara yang aman untuk memeriksa akses tulis
        # tanpa mengubah file.
        with open(filepath, 'a+b'):
            pass
        return False
    except (IOError, PermissionError):
        return True

def diagnose_excel_file(filepath: str):
    """Menjalankan diagnostik pada file Excel/CSV."""
    logging.info(f"Menjalankan diagnostik pada {filepath}...")
    
    if not os.path.exists(filepath):
        logging.error("File tidak ditemukan. Membatalkan diagnostik.")
        return
        
    logging.info("\n=== Pemeriksaan File Dasar ===")
    logging.info(f"Ukuran file: {os.path.getsize(filepath)} bytes")
    logging.info(f"Terakhir diubah: {time.ctime(os.path.getmtime(filepath))}")
    logging.info(f"File terkunci: {is_file_locked(filepath)}")
    
    try:
        logging.info("\n=== Mendiagnosis menggunakan DataHandler ===")
        handler = DataHandler(Path(filepath))
        # Metode diagnose_file di dalam DataHandler perlu direfaktor untuk menggunakan logging juga.
        # Untuk saat ini, kita akan memanggilnya dan mengasumsikan outputnya akan tercetak.
        # (Dalam versi DataHandler yang telah direfaktor, ini akan menggunakan logging)
        logging.info(f"Total baris yang belum diproses menurut DataHandler: {handler.get_unprocessed_data_count()}")
    except Exception as e:
        logging.error(f"Error saat menggunakan DataHandler: {e}", exc_info=True)
        
    try:
        logging.info("\n=== Mendiagnosis menggunakan pandas secara langsung ===")
        df = pd.read_excel(filepath) if filepath.endswith('.xlsx') else pd.read_csv(filepath)
        logging.info(f"Berhasil dimuat dengan pandas. Bentuk (baris, kolom): {df.shape}")
        logging.info(f"Kolom: {', '.join(df.columns.tolist())}")
    except Exception as e:
        logging.error(f"Error saat menggunakan pandas secara langsung: {e}", exc_info=True)

def repair_excel_file(filepath: str):
    """Mencoba memperbaiki file Excel/CSV."""
    if not os.path.exists(filepath):
        logging.error(f"File tidak ditemukan: {filepath}")
        return

    logging.info(f"Mencoba memperbaiki {filepath}...")
    
    backup_path = f"{filepath}.backup-{int(time.time())}"
    try:
        shutil.copy2(filepath, backup_path)
        logging.info(f"Cadangan dibuat di: {backup_path}")
    except Exception as e:
        logging.warning(f"Gagal membuat cadangan: {e}")
        return
    
    try:
        logging.info("Mencoba perbaikan dengan memuat ulang dan menyimpan kembali...")
        df = pd.read_excel(filepath) if filepath.endswith('.xlsx') else pd.read_csv(filepath)
        
        if filepath.endswith('.xlsx'):
            df.to_excel(filepath, index=False, engine='openpyxl')
        else:
            df.to_csv(filepath, index=False)
            
        logging.info("Perbaikan selesai. File berhasil dimuat ulang dan disimpan kembali.")
    except Exception as e:
        logging.error(f"Error selama proses perbaikan: {e}", exc_info=True)
        logging.info(f"File asli Anda aman di cadangan: {backup_path}")

def main():
    parser = argparse.ArgumentParser(description='Alat Utilitas Excel untuk sistem otomatisasi')
    parser.add_argument('command', choices=['diagnose', 'repair', 'check-lock'],
                        help='Perintah yang akan dieksekusi')
    parser.add_argument('filepath', help='Path ke file Excel atau CSV')
    
    args = parser.parse_args()
    
    if args.command == 'diagnose':
        diagnose_excel_file(args.filepath)
    elif args.command == 'repair':
        repair_excel_file(args.filepath)
    elif args.command == 'check-lock':
        if is_file_locked(args.filepath):
            # Menggunakan print di sini karena ini adalah output langsung, bukan pesan log
            print(f"TERKUNCI: File '{args.filepath}' sedang digunakan oleh proses lain.")
            sys.exit(1) # Keluar dengan kode error untuk skrip otomatisasi
        else:
            print(f"AMAN: File '{args.filepath}' tidak terkunci.")
            sys.exit(0) # Keluar dengan kode sukses

if __name__ == '__main__':
    main()