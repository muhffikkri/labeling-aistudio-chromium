# tests/test_failed_row_handler.py
import sys
from pathlib import Path
import pytest
import pandas as pd
import tempfile
import shutil
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.core_logic.failed_row_handler import FailedRowHandler


class TestFailedRowHandler:
    """Test suite untuk FailedRowHandler class"""
    
    def setup_method(self):
        """Setup untuk setiap test method"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.log_folder = self.temp_dir / "log_session"
        self.log_folder.mkdir(exist_ok=True)
        self.source_filename = "test_data"
        
    def teardown_method(self):
        """Cleanup setelah setiap test method"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_init_creates_correct_filepath(self):
        """Test inisialisasi membuat filepath yang benar"""
        handler = FailedRowHandler(self.log_folder, self.source_filename)
        
        expected_path = self.log_folder / f"failed_rows_for_{self.source_filename}.xlsx"
        assert handler.file_path == expected_path
        assert handler.failed_rows == []
    
    def test_add_failed_row_single(self):
        """Test menambahkan satu baris gagal"""
        handler = FailedRowHandler(self.log_folder, self.source_filename)
        
        with patch('logging.warning') as mock_log:
            handler.add_failed_row(
                original_text="Teks sample yang gagal",
                invalid_label="BINGUNG", 
                justification="Alasan yang tidak jelas",
                reason="Validasi Gagal"
            )
        
        assert len(handler.failed_rows) == 1
        failed_row = handler.failed_rows[0]
        
        assert failed_row["full_text"] == "Teks sample yang gagal"
        assert failed_row["invalid_label"] == "BINGUNG"
        assert failed_row["justification"] == "Alasan yang tidak jelas"
        assert failed_row["failure_reason"] == "Validasi Gagal"
        
        # Check logging
        mock_log.assert_called_once()
        call_args = mock_log.call_args[0][0]
        assert "Validasi Gagal" in call_args
        assert "Teks sample yang gagal" in call_args
    
    def test_add_failed_row_multiple(self):
        """Test menambahkan beberapa baris gagal"""
        handler = FailedRowHandler(self.log_folder, self.source_filename)
        
        # Add first failed row
        handler.add_failed_row("Teks 1", "LABEL1", "Justifikasi 1", "Reason 1")
        
        # Add second failed row
        handler.add_failed_row("Teks 2", "LABEL2", "Justifikasi 2", "Reason 2")
        
        assert len(handler.failed_rows) == 2
        assert handler.failed_rows[0]["full_text"] == "Teks 1"
        assert handler.failed_rows[1]["full_text"] == "Teks 2"
    
    def test_add_failed_row_long_text_truncation_in_log(self):
        """Test bahwa teks panjang dipotong dalam log"""
        handler = FailedRowHandler(self.log_folder, self.source_filename)
        
        long_text = "A" * 100  # Text lebih dari 50 karakter
        
        with patch('logging.warning') as mock_log:
            handler.add_failed_row(long_text, "LABEL", "Justifikasi", "Reason")
        
        # Full text should be stored
        assert handler.failed_rows[0]["full_text"] == long_text
        
        # But log should show truncated version
        call_args = mock_log.call_args[0][0]
        assert "A" * 50 + "..." in call_args
    
    def test_save_to_file_with_failed_rows(self):
        """Test menyimpan baris gagal ke file Excel"""
        handler = FailedRowHandler(self.log_folder, self.source_filename)
        
        # Add some failed rows
        handler.add_failed_row("Teks 1", "INVALID1", "Justifikasi 1", "Reason 1")
        handler.add_failed_row("Teks 2", "INVALID2", "Justifikasi 2", "Reason 2")
        
        with patch('logging.info') as mock_log:
            handler.save_to_file()
        
        # Check file was created
        assert handler.file_path.exists()
        
        # Check file content
        df = pd.read_excel(handler.file_path)
        assert len(df) == 2
        assert list(df.columns) == ["full_text", "invalid_label", "justification", "failure_reason"]
        assert df.iloc[0]["full_text"] == "Teks 1"
        assert df.iloc[1]["invalid_label"] == "INVALID2"
        
        # Check logging
        mock_log.assert_any_call(f"Menyimpan 2 baris gagal ke: {handler.file_path}")
        mock_log.assert_any_call("File baris gagal berhasil disimpan.")
        
        # Check that failed_rows list is cleared after save
        assert len(handler.failed_rows) == 0
    
    def test_save_to_file_no_failed_rows(self):
        """Test save_to_file ketika tidak ada baris gagal"""
        handler = FailedRowHandler(self.log_folder, self.source_filename)
        
        with patch('logging.info') as mock_log:
            handler.save_to_file()
        
        # No file should be created
        assert not handler.file_path.exists()
        
        # Should log that no rows to save
        mock_log.assert_called_once_with("Tidak ada baris gagal untuk disimpan.")
    
    def test_save_to_file_excel_write_error(self):
        """Test error handling saat gagal menulis Excel"""
        handler = FailedRowHandler(self.log_folder, self.source_filename)
        
        # Add a failed row
        handler.add_failed_row("Teks", "LABEL", "Justifikasi", "Reason")
        
        # Mock pandas to_excel to raise an exception
        with patch.object(pd.DataFrame, 'to_excel', side_effect=Exception("Disk full")), \
             patch('logging.error') as mock_error_log:
            
            handler.save_to_file()
        
        # Should log error but not raise exception
        mock_error_log.assert_called_once()
        error_call = mock_error_log.call_args[0][0]
        assert "Terjadi error saat menyimpan file baris gagal" in error_call
        assert "Disk full" in str(mock_error_log.call_args)
    
    def test_save_to_file_overwrite_existing(self):
        """Test bahwa save_to_file menimpa file yang sudah ada"""
        handler = FailedRowHandler(self.log_folder, self.source_filename)
        
        # Create initial file with 1 row
        handler.add_failed_row("Old text", "OLD_LABEL", "Old justification", "Old reason")
        handler.save_to_file()
        
        # Verify initial file
        df1 = pd.read_excel(handler.file_path)
        assert len(df1) == 1
        assert df1.iloc[0]["full_text"] == "Old text"
        
        # Add new failed rows
        handler.add_failed_row("New text 1", "NEW_LABEL1", "New justification 1", "New reason 1")
        handler.add_failed_row("New text 2", "NEW_LABEL2", "New justification 2", "New reason 2")
        handler.save_to_file()
        
        # Verify file was overwritten, not appended
        df2 = pd.read_excel(handler.file_path)
        assert len(df2) == 2  # Should be 2, not 3 (overwrite, not append)
        assert df2.iloc[0]["full_text"] == "New text 1"
        assert df2.iloc[1]["full_text"] == "New text 2"
        
        # Old data should not be present
        assert "Old text" not in df2["full_text"].values
    
    def test_file_path_construction_special_characters(self):
        """Test konstruksi path dengan karakter khusus dalam filename"""
        special_filename = "file-with_special.chars"
        handler = FailedRowHandler(self.log_folder, special_filename)
        
        expected_path = self.log_folder / f"failed_rows_for_{special_filename}.xlsx"
        assert handler.file_path == expected_path
    
    def test_dataframe_structure(self):
        """Test struktur DataFrame yang disimpan"""
        handler = FailedRowHandler(self.log_folder, self.source_filename)
        
        # Add failed row with various data types
        handler.add_failed_row(
            original_text="Sample text with émoji 😊",
            invalid_label="WEIRD_LABEL",
            justification="Justifikasi dengan teks unicode: áéíóú",
            reason="Unicode handling test"
        )
        
        handler.save_to_file()
        
        # Read back and verify structure and content
        df = pd.read_excel(handler.file_path)
        
        # Check columns
        expected_columns = ["full_text", "invalid_label", "justification", "failure_reason"]
        assert list(df.columns) == expected_columns
        
        # Check Unicode handling
        assert df.iloc[0]["full_text"] == "Sample text with émoji 😊"
        assert df.iloc[0]["justification"] == "Justifikasi dengan teks unicode: áéíóú"
    
    def test_concurrent_failed_row_additions(self):
        """Test menambahkan baris gagal dalam urutan yang berbeda"""
        handler = FailedRowHandler(self.log_folder, self.source_filename)
        
        # Add rows in different patterns
        for i in range(5):
            handler.add_failed_row(
                original_text=f"Teks {i}",
                invalid_label=f"LABEL_{i}",
                justification=f"Justifikasi {i}",
                reason=f"Reason {i}"
            )
        
        assert len(handler.failed_rows) == 5
        
        # Verify order is preserved
        for i in range(5):
            assert handler.failed_rows[i]["full_text"] == f"Teks {i}"
            assert handler.failed_rows[i]["invalid_label"] == f"LABEL_{i}"
    
    def test_empty_strings_handling(self):
        """Test handling string kosong"""
        handler = FailedRowHandler(self.log_folder, self.source_filename)
        
        handler.add_failed_row("", "", "", "")
        handler.save_to_file()
        
        df = pd.read_excel(handler.file_path)
        assert len(df) == 1
        
        # Empty strings should be preserved
        assert df.iloc[0]["full_text"] == ""
        assert df.iloc[0]["invalid_label"] == ""
        assert df.iloc[0]["justification"] == ""
        assert df.iloc[0]["failure_reason"] == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])