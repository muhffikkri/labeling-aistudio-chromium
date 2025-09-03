# Untuk menjalankan diagnostik

python -m tools.excel_utility diagnose "datasets/nama_file_anda.xlsx"

# Untuk mencoba perbaikan

python -m tools.excel_utility repair "datasets/nama_file_anda.xlsx"

# Untuk memeriksa kunci file

python -m tools.excel_utility check-lock "datasets/nama_file_anda.xlsx"

# Menjalankan perbaikan dengan pengaturan default (membuat backup)

python -m tools.fix_excel_structure "datasets/nama_file_anda.xlsx"

# Menjalankan perbaikan dan juga menghapus kolom tambahan

python -m tools.fix_excel_structure "datasets/nama_file_anda.xlsx" --remove-extra
