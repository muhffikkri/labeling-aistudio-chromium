# Panduan Menjalankan Tes

```bash
pytest
```

Proyek ini dilengkapi dengan serangkaian tes otomatis untuk memastikan bahwa komponen-komponen logika inti berfungsi seperti yang diharapkan. Menjalankan tes ini adalah cara yang baik untuk memverifikasi instalasi Anda dan memastikan tidak ada yang rusak setelah melakukan perubahan kode.

---

### Prasyarat

Kerangka kerja pengujian yang digunakan adalah `pytest`.  
Jika belum terinstal di lingkungan virtual Anda, instal dengan perintah berikut:

```bash
pip install pytest
```

---

### Cara Menjalankan Tes

1. Pastikan lingkungan virtual Anda (`venv`) aktif.
2. Arahkan terminal Anda ke **direktori root proyek**.
3. Jalankan perintah berikut:

```bash
pytest
```

`pytest` akan secara otomatis menemukan semua file tes (yang bernama `test_*.py`) dan menjalankan semua fungsi tes (yang bernama `test_*()`) di dalamnya.

---

### Hasil yang Diharapkan

- **Jika Semua Tes Lulus:**
  Anda akan melihat output berwarna hijau dengan ringkasan di bagian akhir yang mengatakan sesuatu seperti:

  ```
  ======== X passed in Ys ========
  ```

  Ini berarti semua komponen yang diuji berfungsi dengan benar.

- **Jika Ada Tes yang Gagal:**
  Anda akan melihat output berwarna merah dengan detail tentang tes mana yang gagal dan `assert` mana yang tidak terpenuhi.
  Ini menunjukkan adanya masalah atau regresi dalam kode yang perlu diperbaiki sebelum melanjutkan.
