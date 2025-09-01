"""
Script sederhana untuk memeriksa struktur file Excel dan menulis hasilnya ke file.
"""
import pandas as pd
import os

def check_excel_file(excel_path, output_file="excel_check_result.txt"):
    try:
        with open(output_file, 'w') as f:
            f.write(f"Memeriksa file: {excel_path}\n")
            
            if not os.path.exists(excel_path):
                f.write(f"ERROR: File {excel_path} tidak ditemukan!\n")
                return
                
            # Baca file Excel
            df = pd.read_excel(excel_path)
            
            f.write(f"Total baris: {len(df)}\n")
            f.write(f"Kolom yang tersedia: {', '.join(df.columns.tolist())}\n\n")
            
            # Check for unprocessed rows
            if 'label' in df.columns and 'justification' in df.columns:
                unprocessed = df[df['label'].isnull() | df['justification'].isnull()]
                f.write(f"Baris yang belum diproses: {len(unprocessed)} dari {len(df)}\n")
                
                if len(unprocessed) == 0:
                    f.write("MASALAH: Semua baris sudah memiliki nilai label dan justification!\n")
            else:
                f.write("MASALAH: Kolom 'label' atau 'justification' tidak ditemukan!\n")
                
            # Write first 5 rows for debugging
            f.write("\nSample 5 baris pertama:\n")
            f.write(df.head(5).to_string())
            
            f.write("\n\nCheck selesai!\n")
    except Exception as e:
        with open(output_file, 'a') as f:
            f.write(f"ERROR: {str(e)}\n")

if __name__ == "__main__":
    excel_path = "data/ui_2021_01.xlsx"
    check_excel_file(excel_path)
    print(f"Hasil pemeriksaan disimpan dalam file excel_check_result.txt")
