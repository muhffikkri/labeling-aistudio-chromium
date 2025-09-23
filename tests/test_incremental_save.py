#!/usr/bin/env python3
"""
Test script untuk menguji fitur penyimpanan incremental.
Script ini membuat dataset dummy dan menguji apakah:
1. Data disimpan secara incremental
2. Progress bisa di-resume jika terjadi interruption
3. Tidak ada data yang hilang
"""

import pandas as pd
import logging
from pathlib import Path
import sys
import tempfile
import shutil

# Add src to path untuk import
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core_logic.data_handler import DataHandler

def setup_test_logging():
    """Setup logging untuk test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )

def create_test_dataset(file_path: Path, num_rows: int = 10):
    """Membuat dataset test dummy"""
    data = {
        'full_text': [f"Test text number {i+1} for labeling process" for i in range(num_rows)],
        'label': [None] * num_rows,  # Semua unlabeled
        'justification': [None] * num_rows
    }
    
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    logging.info(f"✅ Created test dataset with {num_rows} rows at {file_path}")

def test_incremental_save():
    """Test utama untuk incremental save"""
    logging.info("🧪 Starting incremental save test...")
    
    # Create temporary directory untuk test
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        test_input_file = temp_dir / "test_input.xlsx"
        test_output_dir = temp_dir / "results"
        
        # 1. Buat dataset test
        create_test_dataset(test_input_file, num_rows=5)
        
        # 2. Initialize DataHandler
        logging.info("📋 Testing DataHandler initialization...")
        data_handler = DataHandler(test_input_file, test_output_dir)
        
        # 3. Cek status awal
        progress_info = data_handler.get_progress_info()
        logging.info(f"📊 Initial progress: {progress_info}")
        
        assert progress_info['processed_rows'] == 0, "Should start with 0 processed rows"
        assert progress_info['unprocessed_rows'] == 5, "Should have 5 unprocessed rows"
        
        # 4. Simulate processing first batch
        logging.info("🔄 Simulating first batch processing...")
        fake_results = [
            {"label": "POSITIF", "justification": "Test justification 1"},
            {"label": "NEGATIF", "justification": "Test justification 2"}
        ]
        
        data_handler.update_and_save_data(fake_results, start_index=0)
        data_handler.save_incremental_progress()
        
        # 5. Cek apakah file tersimpan
        assert data_handler.output_filepath.exists(), "Output file should exist after incremental save"
        
        progress_info = data_handler.get_progress_info()
        logging.info(f"📊 Progress after first batch: {progress_info}")
        
        assert progress_info['processed_rows'] == 2, "Should have 2 processed rows"
        assert progress_info['unprocessed_rows'] == 3, "Should have 3 unprocessed rows"
        
        # 6. Test resume functionality - create new DataHandler with same files
        logging.info("🔄 Testing resume functionality...")
        data_handler_2 = DataHandler(test_input_file, test_output_dir)
        
        progress_info_2 = data_handler_2.get_progress_info()
        logging.info(f"📊 Progress after resume: {progress_info_2}")
        
        assert progress_info_2['processed_rows'] == 2, "Should resume with 2 processed rows"
        assert progress_info_2['unprocessed_rows'] == 3, "Should resume with 3 unprocessed rows"
        
        # 7. Continue processing
        logging.info("🔄 Continuing processing after resume...")
        fake_results_2 = [
            {"label": "NETRAL", "justification": "Test justification 3"},
            {"label": "TIDAK RELEVAN", "justification": "Test justification 4"}
        ]
        
        # start_index should still be 0 because we're looking at unprocessed data only
        data_handler_2.update_and_save_data(fake_results_2, start_index=0)
        data_handler_2.save_incremental_progress()
        
        progress_info_final = data_handler_2.get_progress_info()
        logging.info(f"📊 Final progress: {progress_info_final}")
        
        assert progress_info_final['processed_rows'] == 4, "Should have 4 processed rows"
        assert progress_info_final['unprocessed_rows'] == 1, "Should have 1 unprocessed row"
        
        # 8. Verify data integrity
        logging.info("✅ Verifying data integrity...")
        if data_handler_2.output_filepath.suffix == '.xlsx':
            final_df = pd.read_excel(data_handler_2.output_filepath)
        else:
            final_df = pd.read_csv(data_handler_2.output_filepath)
        
        processed_labels = final_df['label'].dropna().tolist()
        expected_labels = ["POSITIF", "NEGATIF", "NETRAL", "TIDAK RELEVAN"]
        
        assert processed_labels == expected_labels, f"Labels mismatch: {processed_labels} vs {expected_labels}"
        
        logging.info("🎉 ALL TESTS PASSED! Incremental save works correctly!")

def test_error_scenarios():
    """Test scenario error dan edge cases"""
    logging.info("🧪 Testing error scenarios...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        test_input_file = temp_dir / "test_input.xlsx"
        test_output_dir = temp_dir / "results"
        
        # Create test dataset
        create_test_dataset(test_input_file, num_rows=3)
        
        # Test dengan file permission error (simulate)
        data_handler = DataHandler(test_input_file, test_output_dir)
        
        # Test save incremental dengan data kosong
        logging.info("📋 Testing incremental save with no processed data...")
        data_handler.save_incremental_progress()  # Should not crash
        
        progress_info = data_handler.get_progress_info()
        assert progress_info['processed_rows'] == 0, "Should still have 0 processed rows"
        
        logging.info("✅ Error scenario tests passed!")

if __name__ == "__main__":
    setup_test_logging()
    
    try:
        test_incremental_save()
        test_error_scenarios()
        logging.info("🎉 ALL INTEGRATION TESTS PASSED!")
        
    except Exception as e:
        logging.error(f"❌ Test failed: {e}", exc_info=True)
        sys.exit(1)