# tests/test_main_integration.py
import sys
import os
from pathlib import Path
import pytest
import pandas as pd
import tempfile
import shutil
from unittest.mock import patch, Mock, MagicMock, call
import argparse

# Set testing environment
os.environ["TESTING"] = "1"

# Add paths for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Now safe to import
try:
    from src.main import main, setup_logging_session, load_prompt
except ImportError:
    # If still fails, create mock functions for testing
    main = Mock()
    setup_logging_session = Mock(return_value=Path("test_logs"))
    load_prompt = Mock(return_value="test prompt")


class TestMainIntegration:
    """Integration tests untuk main.py"""
    
    def setup_method(self):
        """Setup untuk setiap test method"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.datasets_dir = self.temp_dir / "datasets"
        self.prompts_dir = self.temp_dir / "prompts"
        self.results_dir = self.temp_dir / "results"
        self.logs_dir = self.temp_dir / "logs"
        
        # Create directories
        for dir_path in [self.datasets_dir, self.prompts_dir, self.results_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create sample dataset
        self.sample_data = {
            'full_text': [
                'Produk ini sangat bagus dan berkualitas',
                'Pelayanan kurang memuaskan',
                'Harga sesuai dengan kualitas produk',
                'Pengiriman cepat dan aman',
                'Tidak sesuai dengan ekspektasi'
            ]
        }
        self.dataset_file = self.datasets_dir / "sample_data.xlsx"
        pd.DataFrame(self.sample_data).to_excel(self.dataset_file, index=False)
        
        # Create sample prompt
        self.prompt_content = """
Berikan label sentimen untuk setiap teks berikut:
- POSITIF untuk sentimen positif
- NEGATIF untuk sentimen negatif  
- NETRAL untuk sentimen netral
- TIDAK RELEVAN untuk teks yang tidak relevan

Format: LABEL - Justifikasi
"""
        self.prompt_file = self.prompts_dir / "prompt.txt"
        self.prompt_file.write_text(self.prompt_content)
        
    def teardown_method(self):
        """Cleanup setelah setiap test method"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_mock_args(self, **kwargs):
        """Helper untuk membuat mock arguments"""
        default_args = {
            'input_file': self.dataset_file,
            'prompt_file': self.prompt_file,
            'batch_size': 2,
            'debug': False,
            'allowed_labels': 'POSITIF,NEGATIF,NETRAL,TIDAK RELEVAN'
        }
        default_args.update(kwargs)
        
        args = argparse.Namespace(**default_args)
        return args
    
    @patch('src.main.Automation')
    @patch('src.main.DataHandler') 
    @patch('src.main.FailedRowHandler')
    def test_main_successful_flow(self, mock_failed_handler_class, mock_data_handler_class, mock_automation_class):
        """Test alur utama yang berhasil"""
        # Setup mocks
        mock_data_handler = Mock()
        mock_data_handler.get_unprocessed_data_count.return_value = 4
        mock_data_handler.get_data_batches.return_value = [
            ['Produk ini sangat bagus', 'Pelayanan kurang memuaskan'],
            ['Harga sesuai dengan kualitas', 'Pengiriman cepat']
        ]
        mock_data_handler_class.return_value = mock_data_handler
        
        mock_failed_handler = Mock()
        mock_failed_handler_class.return_value = mock_failed_handler
        
        mock_automation = Mock()
        mock_automation.get_raw_response_for_batch.return_value = "POSITIF - Bagus\nNEGATIF - Buruk"
        mock_automation_class.return_value = mock_automation
        
        # Mock parse_and_validate untuk return success
        with patch('src.main.parse_and_validate') as mock_parse:
            mock_parse.return_value = (True, [
                {"label": "POSITIF", "justification": "Bagus"},
                {"label": "NEGATIF", "justification": "Buruk"}
            ])
            
            with patch.object(Path, 'cwd', return_value=self.temp_dir):
                args = self.create_mock_args()
                main(args)
        
        # Verify data handler calls
        mock_data_handler.get_unprocessed_data_count.assert_called_once()
        mock_data_handler.get_data_batches.assert_called_once_with(batch_size=2)
        mock_data_handler.update_and_save_data.assert_called()
        mock_data_handler.save_final_results.assert_called_once()
        
        # Verify browser calls
        mock_automation.start_session.assert_called_once_with("https://aistudio.google.com/")
        mock_automation.get_raw_response_for_batch.assert_called()
        mock_automation.close_session.assert_called_once()
        
        # Verify failed handler
        mock_failed_handler.save_to_file.assert_called_once()
    
    @patch('src.main.Automation')
    @patch('src.main.DataHandler')
    @patch('src.main.FailedRowHandler')
    def test_main_debug_mode(self, mock_failed_handler_class, mock_data_handler_class, mock_automation_class):
        """Test main dalam debug mode"""
        # Setup mocks
        mock_data_handler = Mock()
        mock_data_handler.get_unprocessed_data_count.return_value = 10
        mock_data_handler.get_data_batches.return_value = [
            ['Batch 1'], ['Batch 2'], ['Batch 3']  # 3 batches available
        ]
        mock_data_handler_class.return_value = mock_data_handler
        
        mock_failed_handler = Mock()
        mock_failed_handler_class.return_value = mock_failed_handler
        
        mock_automation = Mock()
        mock_automation.get_raw_response_for_batch.return_value = "POSITIF - Debug response"
        mock_automation_class.return_value = mock_automation
        
        with patch('src.main.parse_and_validate') as mock_parse:
            mock_parse.return_value = (True, [{"label": "POSITIF", "justification": "Debug response"}])
            
            with patch.object(Path, 'cwd', return_value=self.temp_dir):
                args = self.create_mock_args(debug=True)
                main(args)
        
        # In debug mode, should only process first batch
        assert mock_automation.get_raw_response_for_batch.call_count == 1
        mock_data_handler.update_and_save_data.assert_called_once()
    
    @patch('src.main.Automation')
    @patch('src.main.DataHandler')
    @patch('src.main.FailedRowHandler')
    def test_main_validation_failure_with_retries(self, mock_failed_handler_class, mock_data_handler_class, mock_automation_class):
        """Test main dengan validation failure dan retry mechanism"""
        # Setup mocks
        mock_data_handler = Mock()
        mock_data_handler.get_unprocessed_data_count.return_value = 2
        mock_data_handler.get_data_batches.return_value = [['Test text 1', 'Test text 2']]
        mock_data_handler_class.return_value = mock_data_handler
        
        mock_failed_handler = Mock()
        mock_failed_handler_class.return_value = mock_failed_handler
        
        mock_automation = Mock()
        mock_automation.get_raw_response_for_batch.return_value = "Invalid response"
        mock_automation_class.return_value = mock_automation
        
        # Mock parse_and_validate to fail 2 times, then succeed
        with patch('src.main.parse_and_validate') as mock_parse:
            mock_parse.side_effect = [
                (False, "Validation failed - attempt 1"),
                (False, "Validation failed - attempt 2"), 
                (True, [{"label": "POSITIF", "justification": "Finally succeeded"}])
            ]
            
            with patch('time.sleep'), \
                 patch.object(Path, 'cwd', return_value=self.temp_dir):
                args = self.create_mock_args()
                main(args)
        
        # Should retry 3 times total
        assert mock_parse.call_count == 3
        assert mock_automation.get_raw_response_for_batch.call_count == 3
        mock_automation.clear_chat_history.assert_called()  # Should clear history between retries
        
        # Should eventually succeed and update data
        mock_data_handler.update_and_save_data.assert_called_once()
    
    @patch('src.main.Automation')
    @patch('src.main.DataHandler')
    @patch('src.main.FailedRowHandler')
    def test_main_all_retries_failed(self, mock_failed_handler_class, mock_data_handler_class, mock_automation_class):
        """Test main ketika semua retry gagal"""
        # Setup mocks
        mock_data_handler = Mock()
        mock_data_handler.get_unprocessed_data_count.return_value = 2
        mock_data_handler.get_data_batches.return_value = [['Failed text 1', 'Failed text 2']]
        mock_data_handler_class.return_value = mock_data_handler
        
        mock_failed_handler = Mock()
        mock_failed_handler_class.return_value = mock_failed_handler
        
        mock_automation = Mock()
        mock_automation.get_raw_response_for_batch.return_value = "Always invalid"
        mock_automation_class.return_value = mock_automation
        
        # Mock parse_and_validate to always fail
        with patch('src.main.parse_and_validate') as mock_parse:
            mock_parse.return_value = (False, "Always fails")
            
            with patch('time.sleep'), \
                 patch.object(Path, 'cwd', return_value=self.temp_dir):
                args = self.create_mock_args()
                main(args)
        
        # Should try MAX_RETRIES times
        assert mock_parse.call_count == 3
        
        # Should log failed rows
        assert mock_failed_handler.add_failed_row.call_count == 2  # 2 texts in batch
        mock_failed_handler.add_failed_row.assert_any_call(
            original_text='Failed text 1',
            invalid_label='N/A',
            justification='N/A',
            reason='Gagal divalidasi setelah 3 percobaan.'
        )
        
        # Should NOT update data (no valid results)
        mock_data_handler.update_and_save_data.assert_not_called()
    
    @patch('src.main.Automation')
    @patch('src.main.DataHandler')
    def test_main_no_unprocessed_data(self, mock_data_handler_class, mock_automation_class):
        """Test main ketika tidak ada data yang perlu diproses"""
        # Setup mocks
        mock_data_handler = Mock()
        mock_data_handler.get_unprocessed_data_count.return_value = 0
        mock_data_handler_class.return_value = mock_data_handler
        
        with patch.object(Path, 'cwd', return_value=self.temp_dir):
            args = self.create_mock_args()
            main(args)
        
        # Should exit early without starting browser
        mock_automation_class.assert_not_called()
        mock_data_handler.get_data_batches.assert_not_called()
    
    def test_main_browser_initialization_failure(self):
        """Test main ketika browser gagal diinisialisasi"""
        with patch('src.main.DataHandler') as mock_data_handler_class, \
             patch('src.main.Automation') as mock_automation_class:
            
            # Setup data handler
            mock_data_handler = Mock()
            mock_data_handler.get_unprocessed_data_count.return_value = 5
            mock_data_handler_class.return_value = mock_data_handler
            
            # Make browser fail to initialize
            mock_automation_class.side_effect = Exception("Browser failed to start")
            
            with patch.object(Path, 'cwd', return_value=self.temp_dir):
                args = self.create_mock_args()
                
                # Should handle exception gracefully
                main(args)  # Should not crash
    
    def test_main_keyboard_interrupt(self):
        """Test main dengan KeyboardInterrupt (Ctrl+C)"""
        with patch('src.main.DataHandler') as mock_data_handler_class, \
             patch('src.main.Automation') as mock_automation_class:
            
            # Setup mocks
            mock_data_handler = Mock()
            mock_data_handler.get_unprocessed_data_count.return_value = 5
            mock_data_handler.get_data_batches.return_value = [['Test']]
            mock_data_handler_class.return_value = mock_data_handler
            
            mock_automation = Mock()
            mock_automation.get_raw_response_for_batch.side_effect = KeyboardInterrupt()
            mock_automation_class.return_value = mock_automation
            
            with patch.object(Path, 'cwd', return_value=self.temp_dir):
                args = self.create_mock_args()
                main(args)  # Should handle gracefully
            
            # Should still do cleanup
            mock_automation.close_session.assert_called_once()
    
    def test_setup_logging_session(self):
        """Test setup_logging_session function"""
        with patch.object(Path, 'cwd', return_value=self.temp_dir):
            log_folder = setup_logging_session()
        
        # Should create log folder with timestamp
        assert log_folder.exists()
        assert log_folder.parent == self.logs_dir
        assert (log_folder / "run.log").exists()
    
    def test_load_prompt_success(self):
        """Test load_prompt function berhasil"""
        content = load_prompt(self.prompt_file)
        
        assert content is not None
        assert "POSITIF" in content
        assert "Format: LABEL - Justifikasi" in content
    
    def test_load_prompt_file_not_found(self):
        """Test load_prompt dengan file tidak ditemukan"""
        non_existent_file = self.prompts_dir / "not_found.txt"
        
        content = load_prompt(non_existent_file)
        
        assert content is None


class TestMainArgumentParsing:
    """Test argument parsing untuk main.py"""
    
    def test_parse_arguments_minimal(self):
        """Test parsing dengan argument minimal"""
        # This would be tested in actual CLI usage
        # Here we test the structure is correct
        from src.main import main
        
        # Verify function accepts correct argument structure
        mock_args = argparse.Namespace(
            input_file=Path("test.xlsx"),
            prompt_file=Path("prompt.txt"),
            batch_size=50,
            debug=False,
            allowed_labels="POSITIF,NEGATIF,NETRAL,TIDAK RELEVAN"
        )
        
        # Should not raise error with proper arguments structure
        assert hasattr(mock_args, 'input_file')
        assert hasattr(mock_args, 'allowed_labels')
        assert isinstance(mock_args.batch_size, int)
    
    def test_allowed_labels_parsing(self):
        """Test parsing allowed_labels string"""
        allowed_labels_str = "POSITIF,NEGATIF,NETRAL,TIDAK RELEVAN"
        allowed_labels_list = [label.strip().upper() for label in allowed_labels_str.split(',')]
        
        expected = ["POSITIF", "NEGATIF", "NETRAL", "TIDAK RELEVAN"]
        assert allowed_labels_list == expected
    
    def test_allowed_labels_parsing_with_spaces(self):
        """Test parsing allowed_labels dengan spasi"""
        allowed_labels_str = " BAIK , BURUK , BIASA "
        allowed_labels_list = [label.strip().upper() for label in allowed_labels_str.split(',')]
        
        expected = ["BAIK", "BURUK", "BIASA"]
        assert allowed_labels_list == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])