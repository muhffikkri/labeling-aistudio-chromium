import sys
import time
from pathlib import Path

# Menggunakan pytest sebagai framework pengujian formal
import pytest

# Menambahkan direktori root proyek ke path agar kita bisa mengimpor dari 'src'
# Ini adalah pola standar untuk struktur pengujian
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Impor kelas yang SEBENARNYA yang ingin kita uji
from src.core_logic.browser_automation import Automation

# --- KELAS-KELAS MOCK (SIMULASI) ---
# Kelas-kelas ini mensimulasikan perilaku Playwright tanpa memerlukan browser nyata.

class MockPage:
    """Kelas MockPage untuk mensimulasikan objek Page Playwright."""
    def __init__(self):
        self.start_time = time.time()
        
    def locator(self, selector):
        return MockLocator(self)

class MockLocator:
    """Kelas MockLocator untuk mensimulasikan objek Locator."""
    def __init__(self, page):
        self.page = page
    
    def count(self):
        """Mensimulasikan jumlah elemen. Tombol 'Stop' menghilang setelah 8 detik."""
        elapsed = time.time() - self.page.start_time
        return 0 if elapsed > 8 else 1

# --- FUNGSI TES ---

def test_dynamic_wait_successfully_completes():
    """
    Tes ini memverifikasi bahwa metode _wait_for_generation_to_complete()
    dapat dengan benar mendeteksi penyelesaian dalam skenario yang disimulasikan.
    """
    # 1. ARRANGE (PERSIAPAN)
    # Buat instance dari kelas Automation yang sebenarnya.
    # Argumen constructor tidak penting karena kita akan mengganti objek 'page'.
    automation = Automation(user_data_dir="dummy", log_folder=Path("dummy_logs"))

    # Monkeypatching: Ganti objek 'page' yang sebenarnya dengan simulasi kita.
    # Ini adalah langkah paling penting dalam tes unit ini.
    # Sekarang, ketika metode di `automation` memanggil `self.page`, ia akan
    # memanggil `MockPage` kita, bukan Playwright.
    automation.page = MockPage()
    
    # 2. ACT (EKSEKUSI)
    # Panggil metode PRODUKSI yang sebenarnya yang ingin kita uji.
    print("\nMemulai pengujian pada metode _wait_for_generation_to_complete()...")
    is_complete = automation._wait_for_generation_to_complete()
    
    # 3. ASSERT (VERIFIKASI)
    # Verifikasi bahwa metode tersebut mengembalikan hasil yang diharapkan (True).
    # `assert` akan secara otomatis membuat tes gagal jika kondisinya False.
    print(f"Metode mengembalikan: {is_complete}")
    assert is_complete is True, "Logika penungguan seharusnya mengembalikan True saat penyelesaian terdeteksi."
    print("Tes Lulus: Logika penunggaan berfungsi seperti yang diharapkan.")


# --- CARA MENJALANKAN TES INI ---
# 1. Pastikan Anda telah menginstal pytest:
#    pip install pytest
#
# 2. Buka terminal atau command prompt.
#
# 3. Arahkan ke DIREKTORI ROOT PROYEK Anda (folder yang berisi 'src', 'tests', dll.).
#
# 4. Cukup jalankan perintah berikut:
#    pytest
#
# Pytest akan secara otomatis menemukan dan menjalankan fungsi tes ini.