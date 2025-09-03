# Auto-Labeling dengan Aistudio

Aplikasi ini mengotomatiskan proses pelabelan dataset teks dengan memanfaatkan platform Aistudio dari Google melalui otomatisasi browser. Skrip ini secara cerdas membaca data, berinteraksi dengan antarmuka web Aistudio untuk mendapatkan label, dan menyimpan hasilnya kembali, lengkap dengan logging yang kuat dan penanganan error.

## ✨ Fitur Utama

- **Otomatisasi Browser yang Tangguh**: Menggunakan Playwright untuk interaksi yang andal dengan Aistudio.
- **Logging Berbasis Sesi**: Setiap eksekusi menghasilkan folder log yang unik berisi log teks, screenshot, dan artefak debug lainnya.
- **Validasi & Retry Cerdas**: Secara otomatis memvalidasi respons dari AI dan mencoba ulang jika terjadi kegagalan.
- **Dapat Dikonfigurasi**: Perilaku aplikasi dikontrol melalui argumen baris perintah yang jelas.
- **Alat Bantu CLI**: Dilengkapi dengan seperangkat alat bantu untuk mendiagnosis, memvalidasi, dan memperbaiki file data Anda.

## 🚀 Instalasi & Persiapan

### Prasyarat

- Python 3.8+
- Google Chrome terinstal

### Instalasi

1.  **Clone Repositori**: `git clone <URL_REPOSitori_ANDA>`
2.  **Buat Lingkungan Virtual**: `python -m venv venv`
3.  **Aktifkan Lingkungan**:
    - Windows: `.\venv\Scripts\activate`
    - macOS/Linux: `source venv/bin/activate`
4.  **Instal Dependensi**: `pip install -r requirements.txt`

### Konfigurasi

1.  **Dataset**: Tempatkan file `.xlsx` atau `.csv` Anda di dalam folder `datasets/`. Pastikan ada kolom bernama `full_text`.
2.  **Prompt**: Edit file di dalam folder `prompts/` (misalnya `prompt.txt`) dengan instruksi untuk model AI.

## 🏃‍♀️ Panduan Lengkap

Untuk instruksi yang lebih detail, silakan merujuk ke panduan berikut:

- **[Panduan Menjalankan Aplikasi Utama](GUIDE_RUNNING.md)**

  - Cara menjalankan proses pelabelan dari awal hingga akhir.

- **[Panduan Menggunakan Alat Bantu Utilitas](GUIDE_TOOLS.md)**

  - Cara memvalidasi, memperbaiki, dan mendiagnosis file data Anda.

- **[Panduan Debugging dan Pemecahan Masalah](GUIDE_DEBUGGING.md)**

  - Langkah-langkah untuk diikuti jika Anda mengalami error.

- **[Panduan Menjalankan Tes](GUIDE_TESTING.md)**
  - Cara memastikan komponen inti aplikasi berfungsi dengan benar.

## 🤝 Kontribusi

Kontribusi sangat diterima! Silakan ajukan _pull request_ atau buka _issue_.

## 📜 Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT.
