# Panduan Menjalankan Aplikasi Utama

File `src/main.py` adalah titik masuk utama untuk memulai proses pelabelan otomatis. Panduan ini menjelaskan cara menggunakannya.

---

## Struktur Perintah Dasar

Semua perintah dijalankan dari **direktori root proyek** Anda.

```bash
python src/main.py [ARGUMEN]
```

### Argumen Baris Perintah

Anda dapat mengontrol perilaku aplikasi menggunakan argumen berikut:

| Argumen         | Deskripsi                                                                        | Wajib? | Default              |
| --------------- | -------------------------------------------------------------------------------- | ------ | -------------------- |
| `--input-file`  | Path ke file dataset Anda di dalam folder `datasets/`.                           | Ya     | -                    |
| `--prompt-file` | Path ke file prompt Anda.                                                        | Tidak  | `prompts/prompt.txt` |
| `--batch-size`  | Jumlah baris yang akan diproses dalam satu batch.                                | Tidak  | 50                   |
| `--debug`       | Mengaktifkan mode debug. Aplikasi hanya akan memproses satu batch lalu berhenti. | Tidak  | -                    |

---

### Contoh Penggunaan

#### 1. Menjalankan Proses Penuh

Ini adalah cara paling umum untuk menjalankan aplikasi. Ia akan memproses semua baris yang belum dilabeli di file input Anda.

```bash
python src/main.py --input-file "datasets/data_untuk_label.xlsx"
```

#### 2. Menjalankan dengan Ukuran Batch Kustom

Jika Anda mengalami error _"permission denied"_ atau ingin mempercepat/memperlambat proses, Anda dapat menyesuaikan ukuran batch.

```bash
python src/main.py --input-file "datasets/data_untuk_label.xlsx" --batch-size 25
```

#### 3. Menjalankan dalam Mode Debug

Gunakan ini untuk dengan cepat menguji apakah alur kerja berfungsi atau untuk mendiagnosis masalah tanpa harus menunggu seluruh dataset selesai.

```bash
python src/main.py --input-file "datasets/data_untuk_label.xlsx" --debug
```

---

## Apa yang Diharapkan

Saat berjalan, Anda akan melihat log status muncul di terminal Anda.
Setelah selesai, periksa folder `results/` untuk file output Anda dan folder `logs/` untuk detail eksekusi.
