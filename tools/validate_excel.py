import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any

import pandas as pd

# Konfigurasi logging dasar untuk alat bantu CLI.
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def validate_excel_columns(file_path: str) -> Dict[str, Any]:
    """
    Memvalidasi struktur kolom file Excel/CSV agar kompatibel dengan otomatisasi.

    Args:
        file_path (str): Path ke file Excel atau CSV.

    Returns:
        Dict: Kamus berisi hasil validasi yang terstruktur.
    """
    results = {
        "valid": False,
        "issues": [],
        "column_status": {},
        "unprocessed_count": 0
    }
    
    filepath_obj = Path(file_path)
    if not filepath_obj.is_file():
        results["issues"].append(f"File tidak ditemukan: {file_path}")
        return results
        
    try:
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            results["issues"].append("Format file tidak didukung. Harap gunakan .xlsx atau .csv")
            return results
    except Exception as e:
        results["issues"].append(f"Error saat membuka file: {e}")
        return results
        
    if df.empty:
        results["issues"].append("File kosong (tidak berisi baris data).")
        return results
    
    # Skema kolom yang diperlukan dan nama alternatifnya
    required_schema = {
        "full_text": {"alias": ["prompt", "question", "text"], "required": True},
        "label": {"alias": ["classification", "category"], "required": True}, 
        "justification": {"alias": ["explanation", "reason"], "required": True}
    }
    
    available_columns = set(df.columns)
    
    for col, info in required_schema.items():
        found = False
        used_name = None
        
        if col in available_columns:
            found = True
            used_name = col
        else:
            for alias in info["alias"]:
                if alias in available_columns:
                    found = True
                    used_name = alias
                    results["issues"].append(f"INFO: Menggunakan kolom '{alias}' sebagai '{col}'.")
                    break
                    
        results["column_status"][col] = {
            "found": found,
            "used_name": used_name,
            "required": info["required"]
        }
        
        if not found and info["required"]:
            results["issues"].append(f"ERROR: Kolom wajib hilang: '{col}' atau alternatifnya {info['alias']}.")
    
    if any(not status["found"] and status["required"] for status in results["column_status"].values()):
        return results
    
    # Hitung baris yang belum diproses dengan logika yang lebih baik
    if results["column_status"]["label"]["found"] and results["column_status"]["justification"]["found"]:
        label_col = results["column_status"]["label"]["used_name"]
        just_col = results["column_status"]["justification"]["used_name"]
        
        def is_empty(val):
            return pd.isna(val) or (isinstance(val, str) and not val.strip())
            
        label_empty = df[label_col].apply(is_empty)
        just_empty = df[just_col].apply(is_empty)
        results["unprocessed_count"] = (label_empty | just_empty).sum()
    
    # Jika tidak ada error fatal (kolom hilang), anggap valid
    if not any("ERROR:" in issue for issue in results["issues"]):
        results["valid"] = True
    
    return results

def main():
    parser = argparse.ArgumentParser(
        description='Memvalidasi struktur file Excel/CSV untuk sistem otomatisasi.'
    )
    parser.add_argument('filepath', help='Path ke file Excel atau CSV yang akan divalidasi.')
    args = parser.parse_args()
    
    results = validate_excel_columns(args.filepath)
    
    logging.info(f"\n===== HASIL VALIDASI UNTUK {args.filepath} =====")
    
    if results['valid']:
        logging.info("Status: ✅ Valid untuk otomatisasi.")
    else:
        logging.error("Status: ❌ Tidak valid untuk otomatisasi.")
    
    if results["issues"]:
        logging.info("\nDetail dan Isu yang Ditemukan:")
        for issue in results["issues"]:
            if "ERROR:" in issue:
                logging.error(f"- {issue}")
            else:
                logging.warning(f"- {issue}")

    logging.info("\nStatus Kolom:")
    for col, status in results["column_status"].items():
        if status["found"]:
            logging.info(f"  ✓ {col}: Ditemukan (sebagai '{status['used_name']}')")
        elif status["required"]:
            logging.error(f"  ✗ {col}: Hilang (Wajib)")
        else:
            logging.warning(f"  - {col}: Hilang (Opsional)")
    
    logging.info(f"\nBaris yang belum diproses: {results['unprocessed_count']}")
    logging.info("\n===== AKHIR VALIDASI =====")

if __name__ == "__main__":
    main()