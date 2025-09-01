"""
Script untuk memeriksa struktur file Excel yang digunakan.
"""
import pandas as pd
import sys

def check_excel_structure(file_path):
    """
    Memeriksa struktur file Excel dan menampilkan informasi penting.
    """
    print(f"\nMemeriksa file: {file_path}")
    try:
        # Baca file Excel
        df = pd.read_excel(file_path)
        
        # Informasi umum
        print(f"\nInformasi Umum:")
        print(f"Total baris: {len(df)}")
        print(f"Total kolom: {len(df.columns)}")
        print(f"Kolom yang tersedia: {', '.join(df.columns.tolist())}")
        
        # Cek kolom yang diperlukan
        required_columns = ['full_text', 'label', 'justification']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"\nPERINGATAN: Kolom yang diperlukan tidak ditemukan: {', '.join(missing_columns)}")
            print("File Excel harus memiliki kolom 'full_text', 'label', dan 'justification'")
        else:
            print("\nSemua kolom yang diperlukan tersedia.")
        
        # Cek baris yang belum diproses
        if 'label' in df.columns and 'justification' in df.columns:
            unprocessed = df[df['label'].isnull() | df['justification'].isnull()]
            print(f"\nBaris yang belum diproses: {len(unprocessed)} dari {len(df)}")
            
            if len(unprocessed) == 0:
                print("\nMASALAH: Semua baris telah memiliki nilai label dan justification!")
                print("Ini adalah alasan mengapa program mengatakan 'All data has already been processed'")
            else:
                print("\nData yang belum diproses tersedia, program seharusnya dapat memproses data ini.")
        
        # Tampilkan beberapa contoh data
        if len(df) > 0:
            print("\nContoh beberapa baris data:")
            print(df.head(3).to_string())
        
        # Tampilkan contoh data yang belum diproses
        if 'label' in df.columns and 'justification' in df.columns and len(unprocessed) > 0:
            print("\nContoh beberapa baris data yang belum diproses:")
            print(unprocessed.head(3).to_string())
    
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    excel_file = "data/ui_2021_01.xlsx"
    
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
        
    check_excel_structure(excel_file)
    
    print("\n--- Selesai ---\n")
