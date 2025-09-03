# Panduan Menggunakan Alat Bantu Utilitas

Folder `tools/` berisi skrip baris perintah untuk membantu Anda menyiapkan, memvalidasi, dan memperbaiki file data Anda sebelum menjalankan proses pelabelan utama.

**Penting**: Semua alat ini harus dijalankan sebagai modul Python menggunakan flag `-m` dari **direktori root proyek**.

---

### 1. Memvalidasi Struktur File (`validate_excel.py`)

Gunakan alat ini untuk memeriksa apakah file data Anda memiliki kolom yang benar (`full_text`, `label`, `justification`) dan siap untuk diproses.

**Perintah:**

```bash
python -m tools.validate_excel "datasets/nama_file_anda.xlsx"
```

---

### 2. Memperbaiki Struktur File (`fix_excel_structure.py`)

```bash
python -m tools.fix_excel_structure "datasets/nama_file_anda.xlsx"
```

Alat ini dapat secara otomatis memperbaiki masalah umum, seperti:

- Nama kolom yang salah (misalnya, mengubah nama `prompt` menjadi `full_text`).
- Menambahkan kolom yang hilang.

**Perintah Dasar:**

```bash
python -m tools.fix_excel_structure "datasets/nama_file_anda.xlsx"
```

**Opsi Tambahan:**

- `--remove-extra` → Menghapus kolom tambahan yang tidak diperlukan.
- `--no-backup` → Tidak membuat file cadangan sebelum melakukan perubahan.

**Contoh:**

```bash
python -m tools.fix_excel_structure "datasets/nama_file_anda.xlsx" --remove-extra
```

---

### 3. Diagnostik & Perbaikan Umum (`excel_utility.py`)

Ini adalah alat serbaguna dengan beberapa perintah.

**Struktur Perintah:**

```bash
python -m tools.excel_utility [PERINTAH] [FILEPATH]
```

**Perintah yang Tersedia:**

- **diagnose** → Menjalankan pemeriksaan mendalam pada file dan melaporkan statusnya.

  ```bash
  python -m tools.excel_utility diagnose "datasets/nama_file_anda.xlsx"
  ```

- **repair** → Mencoba memperbaiki file yang mungkin rusak dengan memuat dan menyimpannya kembali.

  ```bash
  python -m tools.excel_utility repair "datasets/nama_file_anda.xlsx"
  ```

- **check-lock** → Memeriksa apakah file sedang digunakan atau dikunci oleh proses lain.

  ```bash
  python -m tools.excel_utility check-lock "datasets/nama_file_anda.xlsx"
  ```
