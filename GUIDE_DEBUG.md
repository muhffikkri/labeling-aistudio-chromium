# Panduan Debugging dan Pemecahan Masalah

Jika Anda mengalami error, ikuti panduan ini untuk menemukan sumber masalahnya. Filosofi debugging proyek ini adalah: **semua yang Anda butuhkan ada di dalam folder log sesi.**

---

### Alur Kerja Debugging

#### Langkah 1: Jalankan Ulang dalam Mode Debug

Jalankan aplikasi dengan flag `--debug`. Ini akan memproses hanya satu batch dan menghasilkan folder log yang bersih untuk dianalisis.

```bash
python src/main.py --input-file "datasets/nama_file_anda.xlsx" --debug
```

#### Langkah 2: Temukan Folder Log Sesi

Buka direktori `logs/`. Di dalamnya, Anda akan menemukan folder dengan nama stempel waktu, contoh:
`2025-09-03_12-00-00`.
Buka folder terbaru.

#### Langkah 3: Analisis Artefak Debug (Dalam Urutan Ini)

1. **run.log**

   - Ini adalah titik awal Anda. Buka file ini.
   - Cari pesan **ERROR** atau **CRITICAL** di dekat bagian bawah file. Pesan error dan traceback yang menyertainya akan memberi tahu Anda apa yang salah di dalam kode.
   - Baca juga pesan **WARNING** untuk petunjuk tentang masalah yang tidak fatal.

2. **Screenshots (.png)**

   - Jika log menunjukkan error terkait browser (misalnya, _"Timeout"_ atau _"Gagal mengklik elemen"_), cari file screenshot di folder log (misalnya: `FATAL_ERROR_timeout.png` atau `ERROR_extraction_failed.png`).
   - Gambar ini menunjukkan apa yang dilihat browser pada saat error terjadi.

3. **check*data_batch\_...\_attempt*....txt**

   - Gunakan file ini untuk masalah validasi. Jika log mengatakan _"Validasi Gagal"_, buka file ini.
   - Bandingkan bagian **RAW RESPONSE** (apa yang dikembalikan AI) dengan **FULL PROMPT** (apa yang Anda kirim).
   - Periksa: Apakah formatnya salah? Apakah jumlah barisnya tidak cocok? File ini menjawab pertanyaan-pertanyaan tersebut.

4. **failed_rows_for\_... .xlsx**

   - Jika sebuah batch gagal setelah semua percobaan, baris-baris asli dari batch tersebut akan disimpan di sini.
   - Anda dapat memeriksanya untuk melihat apakah ada data yang aneh di dalam teks yang mungkin menyebabkan masalah.

---

### Skenario Masalah Umum

- **Masalah:** Aplikasi gagal login atau mengalami timeout saat memulai.
  **Solusi:** Periksa screenshot `FATAL_ERROR_timeout.png`. Pastikan Anda dapat login secara manual. Hapus folder `browser_data/` untuk memulai sesi yang bersih.

- **Masalah:** Log mengatakan _"Validasi Gagal: Jumlah baris output tidak sesuai"_.
  **Solusi:** Buka file `check_data_....txt`. Lihat **RAW RESPONSE**. Kemungkinan AI tidak mengembalikan satu baris untuk setiap item input. Anda mungkin perlu menyesuaikan prompt Anda.

- **Masalah:** Log mengatakan _"Validasi Gagal: Ditemukan label tidak valid"_.
  **Solusi:** Buka `check*data_batch\_...\_attempt*....txt`. Lihat **RAW RESPONSE**. AI mungkin mengembalikan label yang tidak ada dalam `ALLOWED_LABELS` di `src/core_logic/validation.py`. Sesuaikan prompt Anda atau tambahkan label baru ke daftar yang diizinkan.
