import argparse
import logging
import os
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Menambahkan blok try-except untuk impor agar memberikan pesan error yang lebih baik
try:
    from tools.validate_excel import validate_excel_columns
except ImportError:
    print("FATAL ERROR: Tidak dapat mengimpor validate_excel. Pastikan Anda menjalankan skrip ini sebagai modul dari direktori root proyek.")
    print("Contoh: python -m tools.fix_excel_structure ...")
    sys.exit(1)

# Konfigurasi logging dasar. Levelnya akan diatur nanti oleh argumen CLI.
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def fix_excel_structure(file_path: str, make_backup=True, remove_extra=False, verbose=True):
    """
    Memperbaiki masalah struktural umum di file Excel/CSV untuk otomatisasi.
    """
    # Atur level logging berdasarkan flag verbose/quiet
    if verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARNING) # Hanya tampilkan peringatan & error jika quiet
    
    if not os.path.exists(file_path):
        logging.error(f"File tidak ditemukan: {file_path}")
        return False
        
    if make_backup:
        backup_path = f"{file_path}.backup-{int(pd.Timestamp.now().timestamp())}"
        try:
            shutil.copy2(file_path, backup_path)
            logging.info(f"Cadangan dibuat di {backup_path}")
        except Exception as e:
            logging.error(f"Tidak dapat membuat cadangan: {e}", exc_info=True)
            return False
    
    try:
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            logging.error(f"Format file tidak didukung: {file_path}")
            return False
    except Exception as e:
        logging.error(f"Gagal membuka file: {e}", exc_info=True)
        return False
    
    # Skema kolom yang diperlukan dan alternatifnya yang umum
    required_schema = {
        "full_text": ["prompt", "question", "text", "content"],
        "label": ["classification", "category", "sentiment"],
        "justification": ["explanation", "reason", "rationale"]
    }
    
    column_mapping = {}  # original_name -> target_name
    columns_to_create = []
    
    logging.info("Menganalisis struktur kolom...")
    for target_col, alternatives in required_schema.items():
        if target_col in df.columns:
            logging.info(f"✓ Kolom '{target_col}' sudah ada.")
            continue
            
        found_alt = False
        for alt_col in alternatives:
            if alt_col in df.columns:
                column_mapping[alt_col] = target_col
                found_alt = True
                logging.warning(f"-> Menemukan alternatif '{alt_col}'. Akan diubah nama menjadi '{target_col}'.")
                break
                
        if not found_alt:
            columns_to_create.append(target_col)
            logging.warning(f"✗ Kolom '{target_col}' tidak ditemukan. Akan dibuat kolom baru.")
    
    if column_mapping:
        df = df.rename(columns=column_mapping)
        logging.info("Berhasil mengubah nama kolom.")
    
    for col in columns_to_create:
        df[col] = np.nan
        if col == "full_text":
            logging.critical("PERHATIAN: Kolom 'full_text' dibuat kosong. Anda harus mengisi data di kolom ini secara manual!")
    
    if remove_extra:
        final_required_cols = list(required_schema.keys())
        extra_columns = [col for col in df.columns if col not in final_required_cols]
        
        if extra_columns:
            logging.info(f"Menghapus {len(extra_columns)} kolom tambahan: {', '.join(extra_columns)}")
            df = df[final_required_cols]
    
    try:
        if file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        elif file_path.endswith('.csv'):
            df.to_csv(file_path, index=False)
        logging.info(f"Berhasil menyimpan perubahan ke {file_path}")
        
        logging.info("Memvalidasi ulang file setelah diperbaiki...")
        fixed_validation = validate_excel_columns(file_path)
        
        if fixed_validation["valid"]:
            logging.info("\n✅ STRUKTUR FILE BERHASIL DIPERBAIKI!")
            return True
        else:
            logging.warning("\n⚠️ Beberapa masalah mungkin masih ada setelah perbaikan:")
            for issue in fixed_validation["issues"]:
                logging.warning(f"- {issue}")
            return False
            
    except Exception as e:
        logging.error(f"Gagal menyimpan file setelah diperbaiki: {e}", exc_info=True)
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Memperbaiki struktur file Excel/CSV agar kompatibel dengan sistem otomatisasi.'
    )
    parser.add_argument('file_path', help='Path ke file Excel atau CSV')
    parser.add_argument('--no-backup', action='store_true', 
                        help='Jangan membuat file cadangan sebelum memperbaiki.')
    parser.add_argument('--remove-extra', action='store_true',
                        help='Hapus kolom-kolom yang tidak diperlukan.')
    parser.add_argument('--quiet', action='store_true',
                        help='Hanya tampilkan output jika ada error atau peringatan penting.')
    
    args = parser.parse_args()
    
    fix_excel_structure(
        args.file_path,
        make_backup=not args.no_backup,
        remove_extra=args.remove_extra,
        verbose=not args.quiet
    )

if __name__ == "__main__":
    main()