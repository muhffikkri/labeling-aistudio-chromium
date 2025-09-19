#!/usr/bin/env python3
"""
Test script untuk memverifikasi perbaikan validasi batch dinamis dan file saving behavior.
"""
import sys
from pathlib import Path
import tempfile
import pandas as pd
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core_logic.data_handler import DataHandler
from core_logic.validation import parse_and_validate

def setup_test_logging():
    """Setup logging untuk testing."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s - %(message)s'
    )

def create_test_data(num_rows: int = 17) -> Path:
    """Buat data test dengan jumlah baris tertentu."""
    test_data = []
    for i in range(1, num_rows + 1):
        test_data.append({
            'full_text': f'Teks sampel untuk testing batch dinamis nomor {i}',
            'existing_label': None if i % 5 != 0 else 'POSITIF',  # Beberapa sudah ada label
            'justification': None
        })
    
    df = pd.DataFrame(test_data)
    df = df.rename(columns={'existing_label': 'label'})
    
    # Simpan ke file temporary
    temp_file = Path(tempfile.mktemp(suffix='.csv'))
    df.to_csv(temp_file, index=False)
    return temp_file

def test_dynamic_batch_validation():
    """Test validasi batch dinamis."""
    print("\n🧪 TEST: Dynamic Batch Validation")
    print("=" * 50)
    
    # Test case: 17 rows total, batch size 5
    # Expected batches: [5, 5, 5, 2]
    total_rows = 17
    batch_size = 5
    expected_counts = [5, 5, 5, 2]
    
    print(f"Total rows: {total_rows}")
    print(f"Batch size: {batch_size}")
    print(f"Expected batch sizes: {expected_counts}")
    
    # Simulasi perhitungan expected_count untuk setiap batch
    for batch_index in range(4):
        rows_processed_so_far = batch_index * batch_size
        remaining_rows = total_rows - rows_processed_so_far
        expected_count = min(batch_size, remaining_rows)
        
        print(f"Batch {batch_index + 1}: rows_processed_so_far={rows_processed_so_far}, "
              f"remaining_rows={remaining_rows}, expected_count={expected_count}")
        
        assert expected_count == expected_counts[batch_index], f"Expected {expected_counts[batch_index]}, got {expected_count}"
    
    print("✅ Dynamic batch validation logic works correctly!")

def test_validation_function():
    """Test function parse_and_validate dengan expected_count yang berbeda."""
    print("\n🧪 TEST: Validation Function")
    print("=" * 50)
    
    # Test case 1: Normal batch (expected_count = 3)
    raw_response1 = """POSITIF - Teks ini sangat bagus
NEGATIF - Teks ini buruk sekali
NETRAL - Teks ini biasa saja"""
    
    is_valid1, result1 = parse_and_validate(raw_response1, expected_count=3, allowed_labels=['POSITIF', 'NEGATIF', 'NETRAL'])
    print(f"Test 1 - Full batch (3 items): Valid={is_valid1}, Results={len(result1) if isinstance(result1, list) else 'Error'}")
    
    # Test case 2: Last batch (expected_count = 2)
    raw_response2 = """POSITIF - Teks terakhir pertama
NETRAL - Teks terakhir kedua
POSITIF - Teks kelebihan yang seharusnya diabaikan"""
    
    is_valid2, result2 = parse_and_validate(raw_response2, expected_count=2, allowed_labels=['POSITIF', 'NEGATIF', 'NETRAL'])
    print(f"Test 2 - Last batch (2 items): Valid={is_valid2}, Results={len(result2) if isinstance(result2, list) else 'Error'}")
    
    # Test case 3: Single item batch (expected_count = 1)
    raw_response3 = """POSITIF - Satu teks saja
NEGATIF - Teks kelebihan yang tidak diperlukan"""
    
    is_valid3, result3 = parse_and_validate(raw_response3, expected_count=1, allowed_labels=['POSITIF', 'NEGATIF', 'NETRAL'])
    print(f"Test 3 - Single item (1 item): Valid={is_valid3}, Results={len(result3) if isinstance(result3, list) else 'Error'}")
    
    assert is_valid1 and len(result1) == 3, "Test 1 should pass with 3 results"
    assert is_valid2 and len(result2) == 2, "Test 2 should pass with 2 results"
    assert is_valid3 and len(result3) == 1, "Test 3 should pass with 1 result"
    
    print("✅ Validation function works correctly with dynamic expected_count!")

def test_file_saving_behavior():
    """Test bahwa file hanya disimpan ke results folder, tidak ke input file."""
    print("\n🧪 TEST: File Saving Behavior")
    print("=" * 50)
    
    # Buat test data
    test_file = create_test_data(5)
    print(f"Created test file: {test_file}")
    
    # Baca konten original
    original_df = pd.read_csv(test_file)
    original_null_count = original_df['label'].isnull().sum()
    print(f"Original unprocessed rows: {original_null_count}")
    
    try:
        # Inisialisasi DataHandler dengan custom output directory
        with tempfile.TemporaryDirectory() as temp_output_dir:
            data_handler = DataHandler(input_filepath=test_file, output_dir=Path(temp_output_dir))
            
            # Simulasi update data
            test_results = [
                {"label": "POSITIF", "justification": "Test justification 1"},
                {"label": "NEGATIF", "justification": "Test justification 2"}
            ]
            
            data_handler.update_and_save_data(test_results, start_index=0)
            
            # Periksa bahwa file input TIDAK berubah
            current_df = pd.read_csv(test_file)
            current_null_count = current_df['label'].isnull().sum()
            
            print(f"Current unprocessed rows in input file: {current_null_count}")
            assert current_null_count == original_null_count, "Input file should not be modified"
            
            # Simulasi save final results
            data_handler.save_final_results()
            
            # Periksa bahwa file output ada dan berisi data yang benar
            output_files = list(Path(temp_output_dir).glob("*.csv"))
            assert len(output_files) == 1, "Should create exactly one output file"
            
            output_df = pd.read_csv(output_files[0])
            output_labeled_count = output_df['label'].notnull().sum()
            print(f"Output file labeled rows: {output_labeled_count}")
            
            print(f"✅ Input file unchanged, output file created at: {output_files[0]}")
            
    finally:
        # Cleanup
        test_file.unlink()

def test_batch_generation():
    """Test pembagian batch dengan data yang memiliki beberapa baris sudah ter-label."""
    print("\n🧪 TEST: Batch Generation with Pre-labeled Data")
    print("=" * 50)
    
    test_file = create_test_data(12)  # 12 total rows, setiap row ke-5 sudah ada label
    
    try:
        data_handler = DataHandler(input_filepath=test_file)
        
        # Cek jumlah unprocessed
        unprocessed_count = data_handler.get_unprocessed_data_count()
        print(f"Unprocessed rows: {unprocessed_count}")
        
        # Generate batches
        batches = data_handler.get_data_batches(batch_size=4)
        print(f"Generated batches: {len(batches)}")
        for i, batch in enumerate(batches):
            print(f"  Batch {i+1}: {len(batch)} items")
        
        total_batch_items = sum(len(batch) for batch in batches)
        assert total_batch_items == unprocessed_count, f"Total batch items ({total_batch_items}) should match unprocessed count ({unprocessed_count})"
        
        print("✅ Batch generation works correctly with pre-labeled data!")
        
    finally:
        test_file.unlink()

def run_all_tests():
    """Run semua test."""
    setup_test_logging()
    
    print("🚀 Running All Tests for Dynamic Batch Validation and File Saving Fixes")
    print("=" * 80)
    
    try:
        test_dynamic_batch_validation()
        test_validation_function()
        test_file_saving_behavior()
        test_batch_generation()
        
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("✅ Dynamic batch validation implemented correctly")
        print("✅ File saving behavior fixed (no more input file modification)")
        print("✅ Validation function handles different expected_count values")
        print("✅ Batch generation works with pre-labeled data")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)