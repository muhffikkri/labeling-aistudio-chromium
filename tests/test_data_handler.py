# tests/test_data_handler.py
import sys
from pathlib import Path
import pytest
import pandas as pd
import tempfile
import shutil
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.core_logic.data_handler import DataHandler


class TestDataHandler:
    """Test suite untuk DataHandler class"""
    
    def setup_method(self):
        """Setup untuk setiap test method"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.sample_data = {
            'full_text': [
                'Teks sampel 1',
                'Teks sampel 2', 
                'Teks sampel 3',
                'Teks sampel 4',
                'Teks sampel 5'
            ],
            'label': [None, None, None, 'POSITIF', 'NEGATIF'],  # 3 unprocessed, 2 processed
            'justification': [None, None, None, 'Alasan positif', 'Alasan negatif']
        }
        
    def teardown_method(self):
        """Cleanup setelah setiap test method"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_sample_excel(self, filename: str, data: dict = None) -> Path:
        """Helper untuk membuat file Excel sample"""
        if data is None:
            data = self.sample_data
        
        filepath = self.temp_dir / filename
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
        return filepath
    
    def create_sample_csv(self, filename: str, data: dict = None) -> Path:
        """Helper untuk membuat file CSV sample"""
        if data is None:
            data = self.sample_data
        
        filepath = self.temp_dir / filename
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        return filepath
    
    def test_init_with_excel_file(self):
        """Test inisialisasi dengan file Excel"""
        excel_path = self.create_sample_excel("test.xlsx")
        
        with patch('pathlib.Path.mkdir'):  # Mock mkdir untuk results folder
            handler = DataHandler(excel_path)
        
        assert handler.input_filepath == excel_path
        assert len(handler.df) == 5
        assert 'full_text' in handler.df.columns
        assert 'label' in handler.df.columns
        assert 'justification' in handler.df.columns
    
    def test_init_with_csv_file(self):
        """Test inisialisasi dengan file CSV"""
        csv_path = self.create_sample_csv("test.csv")
        
        with patch('pathlib.Path.mkdir'):
            handler = DataHandler(csv_path)
        
        assert handler.input_filepath == csv_path
        assert len(handler.df) == 5
    
    def test_init_file_not_found(self):
        """Test handling ketika file tidak ditemukan"""
        non_existent_path = self.temp_dir / "tidak_ada.xlsx"
        
        with pytest.raises(FileNotFoundError):
            DataHandler(non_existent_path)
    
    def test_init_unsupported_format(self):
        """Test handling untuk format file tidak didukung"""
        txt_path = self.temp_dir / "test.txt"
        txt_path.write_text("some text")
        
        with pytest.raises(ValueError, match="Format file tidak didukung"):
            DataHandler(txt_path)
    
    def test_ensure_columns_exist_missing_columns(self):
        """Test penambahan kolom yang hilang"""
        # Buat data tanpa kolom label dan justification
        minimal_data = {'full_text': ['Teks 1', 'Teks 2']}
        excel_path = self.create_sample_excel("minimal.xlsx", minimal_data)
        
        with patch('pathlib.Path.mkdir'), \
             patch.object(DataHandler, 'save_progress') as mock_save:
            handler = DataHandler(excel_path)
        
        # Pastikan kolom ditambahkan
        assert 'label' in handler.df.columns
        assert 'justification' in handler.df.columns
        
        # Pastikan save_progress dipanggil karena ada perubahan
        mock_save.assert_called_once()
    
    def test_get_unprocessed_data_count(self):
        """Test penghitungan data yang belum diproses"""
        excel_path = self.create_sample_excel("test.xlsx")
        
        with patch('pathlib.Path.mkdir'):
            handler = DataHandler(excel_path)
        
        count = handler.get_unprocessed_data_count()
        assert count == 3  # 3 baris dengan label None
    
    def test_get_data_batches(self):
        """Test pembagian data menjadi batch"""
        excel_path = self.create_sample_excel("test.xlsx")
        
        with patch('pathlib.Path.mkdir'):
            handler = DataHandler(excel_path)
        
        batches = handler.get_data_batches(batch_size=2)
        
        # 3 unprocessed items, batch size 2 -> 2 batches
        assert len(batches) == 2
        assert len(batches[0]) == 2  # First batch: 2 items
        assert len(batches[1]) == 1  # Second batch: 1 item
        
        # Check content
        assert batches[0][0] == 'Teks sampel 1'
        assert batches[0][1] == 'Teks sampel 2'
        assert batches[1][0] == 'Teks sampel 3'
    
    def test_get_data_batches_no_unprocessed(self):
        """Test get_data_batches ketika semua data sudah diproses"""
        # Semua data sudah memiliki label
        processed_data = {
            'full_text': ['Teks 1', 'Teks 2'],
            'label': ['POSITIF', 'NEGATIF'],
            'justification': ['Alasan 1', 'Alasan 2']
        }
        excel_path = self.create_sample_excel("processed.xlsx", processed_data)
        
        with patch('pathlib.Path.mkdir'):
            handler = DataHandler(excel_path)
        
        batches = handler.get_data_batches()
        assert len(batches) == 0
    
    def test_get_data_batches_missing_full_text_column(self):
        """Test handling ketika kolom full_text tidak ada"""
        invalid_data = {'other_column': ['data1', 'data2']}
        excel_path = self.create_sample_excel("invalid.xlsx", invalid_data)
        
        with patch('pathlib.Path.mkdir'):
            handler = DataHandler(excel_path)
        
        batches = handler.get_data_batches()
        assert len(batches) == 0
    
    def test_update_and_save_data(self):
        """Test update dan save data dengan hasil labeling"""
        excel_path = self.create_sample_excel("test.xlsx")
        
        with patch('pathlib.Path.mkdir'), \
             patch.object(DataHandler, 'save_progress') as mock_save:
            handler = DataHandler(excel_path)
            mock_save.reset_mock()  # Reset karena __init__ juga memanggil save_progress
        
        # Sample results untuk 2 item pertama yang unprocessed
        results = [
            {"label": "POSITIF", "justification": "Hasil labeling 1"},
            {"label": "NEGATIF", "justification": "Hasil labeling 2"}
        ]
        
        handler.update_and_save_data(results, start_index=0)
        
        # Check bahwa data telah diupdate
        assert handler.df.iloc[0]['label'] == 'POSITIF'
        assert handler.df.iloc[1]['label'] == 'NEGATIF'
        assert handler.df.iloc[0]['justification'] == 'Hasil labeling 1'
        assert handler.df.iloc[1]['justification'] == 'Hasil labeling 2'
        
        # Check yang sudah ada sebelumnya tetap tidak berubah
        assert handler.df.iloc[3]['label'] == 'POSITIF'  # Data yang sudah ada
        assert handler.df.iloc[4]['label'] == 'NEGATIF'  # Data yang sudah ada
        
        # save_progress harus dipanggil
        mock_save.assert_called_once()
    
    def test_save_progress_excel(self):
        """Test save progress untuk file Excel"""
        excel_path = self.create_sample_excel("test.xlsx")
        
        with patch('pathlib.Path.mkdir'):
            handler = DataHandler(excel_path)
        
        # Modify data
        handler.df.iloc[0]['label'] = 'TEST_LABEL'
        
        # Test save
        handler.save_progress()
        
        # Read back and verify
        df_check = pd.read_excel(excel_path)
        assert df_check.iloc[0]['label'] == 'TEST_LABEL'
    
    def test_save_progress_csv(self):
        """Test save progress untuk file CSV"""
        csv_path = self.create_sample_csv("test.csv")
        
        with patch('pathlib.Path.mkdir'):
            handler = DataHandler(csv_path)
        
        # Modify data
        handler.df.iloc[0]['label'] = 'TEST_LABEL'
        
        # Test save
        handler.save_progress()
        
        # Read back and verify
        df_check = pd.read_csv(csv_path)
        assert df_check.iloc[0]['label'] == 'TEST_LABEL'
    
    def test_save_final_results_excel(self):
        """Test save final results untuk Excel"""
        excel_path = self.create_sample_excel("test.xlsx")
        
        with patch('pathlib.Path.mkdir'):
            handler = DataHandler(excel_path)
        
        # Mock the output file path for testing
        original_output = handler.output_filepath
        test_output = self.temp_dir / "output_test.xlsx"
        handler.output_filepath = test_output
        
        handler.save_final_results()
        
        # Verify output file exists and has correct content
        assert test_output.exists()
        df_output = pd.read_excel(test_output)
        assert len(df_output) == 5
        assert 'full_text' in df_output.columns
    
    def test_save_final_results_csv(self):
        """Test save final results untuk CSV"""
        csv_path = self.create_sample_csv("test.csv")
        
        with patch('pathlib.Path.mkdir'):
            handler = DataHandler(csv_path)
        
        # Mock the output file path for testing
        test_output = self.temp_dir / "output_test.csv"
        handler.output_filepath = test_output
        
        handler.save_final_results()
        
        # Verify output file exists and has correct content
        assert test_output.exists()
        df_output = pd.read_csv(test_output)
        assert len(df_output) == 5
        assert 'full_text' in df_output.columns
    
    def test_error_handling_save_progress(self):
        """Test error handling saat save progress gagal"""
        excel_path = self.create_sample_excel("test.xlsx")
        
        with patch('pathlib.Path.mkdir'):
            handler = DataHandler(excel_path)
        
        # Make file read-only to cause save error
        excel_path.chmod(0o444)
        
        # Should not raise exception, just log error
        with patch('logging.error') as mock_log:
            handler.save_progress()
            mock_log.assert_called()
        
        # Restore permissions for cleanup
        excel_path.chmod(0o666)
    
    def test_error_handling_save_final_results(self):
        """Test error handling saat save final results gagal"""
        excel_path = self.create_sample_excel("test.xlsx")
        
        with patch('pathlib.Path.mkdir'):
            handler = DataHandler(excel_path)
        
        # Set invalid output path
        handler.output_filepath = Path("/invalid/path/output.xlsx")
        
        # Should not raise exception, just log error
        with patch('logging.error') as mock_log:
            handler.save_final_results()
            mock_log.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])