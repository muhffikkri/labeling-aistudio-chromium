"""
Skrip sederhana untuk membebaskan file Excel dari kuncian.
"""
import os
import time
import sys
from pathlib import Path

# Daftar file Excel yang ingin dibebaskan
EXCEL_FILES = [
    "data/data_sample_blank.xlsx",
    "data/Book1.xlsx",
    "data/dataset.xlsx"
]

def check_file_access(filepath):
    """Memeriksa apakah file bisa diakses."""
    try:
        if os.path.exists(filepath):
            print(f"File {filepath} ditemukan.")
            # Coba akses file dengan mode akses read-write
            with open(filepath, 'r+b') as f:
                # Hanya baca 1 byte untuk memastikan akses
                data = f.read(1)
                print(f"✓ Berhasil membuka file: {filepath}")
            return True
        else:
            print(f"✗ File tidak ditemukan: {filepath}")
            return False
    except Exception as e:
        print(f"✗ Tidak bisa mengakses file {filepath}: {e}")
        return False

def main():
    print("=== PEMERIKSAAN AKSES FILE EXCEL ===")
    
    for excel_file in EXCEL_FILES:
        print("\n" + "="*50)
        print(f"Memeriksa file: {excel_file}")
        
        # Periksa akses file
        access_ok = check_file_access(excel_file)
        
        if access_ok:
            print(f"✓ File {excel_file} dapat diakses dengan normal.")
        else:
            print(f"✗ File {excel_file} TERKUNCI atau TIDAK TERSEDIA.")
            print("  Saran: ")
            print("  1. Tutup semua aplikasi Python dan Excel")
            print("  2. Jalankan skrip ini lagi")
            print("  3. Jika masih bermasalah, restart komputer")
    
    print("\n" + "="*50)
    print("HASIL KESIMPULAN:")
    print("Jika semua file berhasil diakses (tanda ✓), Anda bisa membuka file Excel secara normal.")
    print("Jika ada file yang tidak bisa diakses (tanda ✗), ikuti saran yang diberikan.")
    
    input("\nTekan Enter untuk keluar...")

if __name__ == "__main__":
    main()
