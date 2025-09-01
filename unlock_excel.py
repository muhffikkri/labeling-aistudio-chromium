"""
Skrip untuk membebaskan file Excel yang terkunci.
Jalankan skrip ini sebelum mencoba membuka file Excel secara manual.
"""
import os
import gc
import sys
import psutil
import time

def kill_python_processes():
    """Menghentikan semua proses Python yang sedang berjalan."""
    print("Menghentikan semua proses Python yang sedang berjalan...")
    for proc in psutil.process_iter(['pid', 'name']):
        if 'python' in proc.info['name'].lower():
            try:
                print(f"Menghentikan proses Python dengan PID: {proc.info['pid']}")
                psutil.Process(proc.info['pid']).terminate()
            except Exception as e:
                print(f"Gagal menghentikan proses: {e}")

def unlock_file(filepath):
    """Berusaha membebaskan file dari kuncian dengan memaksa garbage collection."""
    print(f"Berusaha membebaskan file: {filepath}")
    
    # Paksa garbage collection untuk membebaskan file handle
    gc.collect()
    
    # Tunggu sebentar
    time.sleep(1)
    
    # Periksa apakah file bisa diakses
    try:
        with open(filepath, 'rb') as test_file:
            # Hanya baca sedikit data untuk memverifikasi akses
            test_file.read(1)
            print("✓ File berhasil dibuka")
            return True
    except Exception as e:
        print(f"✗ Masih tidak bisa mengakses file: {e}")
        return False

def main():
    excel_files = [
        "data/data_sample_blank.xlsx",
        "data/Book1.xlsx",
        "data/dataset.xlsx"
    ]
    
    print("=== PROGRAM PEMBEBASAN FILE EXCEL ===")
    print("Skrip ini akan membebaskan file Excel yang terkunci oleh proses Python")
    
    # Hentikan proses Python
    kill_python_processes()
    
    # Tunggu sebentar agar proses-proses benar-benar berhenti
    print("Menunggu proses-proses berhenti...")
    time.sleep(3)
    
    # Coba buka setiap file Excel
    for excel_file in excel_files:
        if os.path.exists(excel_file):
            print(f"\nMemproses file: {excel_file}")
            success = unlock_file(excel_file)
            if success:
                print(f"✓ File {excel_file} sekarang dapat diakses.")
            else:
                print(f"✗ Gagal membebaskan file {excel_file}.")
        else:
            print(f"\nFile {excel_file} tidak ditemukan, melewati.")
    
    print("\n=== SELESAI ===")
    print("Anda sekarang dapat mencoba membuka file Excel secara manual.")
    print("Jika masih tidak bisa, coba restart komputer.")
    
    # Beri waktu pengguna untuk membaca pesan
    input("\nTekan Enter untuk menutup program ini...")

if __name__ == "__main__":
    main()
