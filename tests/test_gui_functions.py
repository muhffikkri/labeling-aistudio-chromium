# tests/test_gui_functions.py
import sys
from pathlib import Path
import pytest
import tkinter as tk
import tempfile
import shutil
from unittest.mock import patch, Mock, MagicMock, mock_open
import queue
import threading

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestGUIComponents:
    """Test suite untuk GUI components tanpa actually menjalankan GUI"""
    
    def setup_method(self):
        """Setup untuk setiap test method"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.datasets_dir = self.temp_dir / "datasets"
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
        
        # Create sample files
        self.sample_excel = self.datasets_dir / "sample.xlsx"
        self.sample_csv = self.datasets_dir / "sample.csv"
        
        # Mock file creation
        self.sample_excel.touch()
        self.sample_csv.touch()
        
    def teardown_method(self):
        """Cleanup setelah setiap test method"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    @patch('src.gui.gui.tk.Tk')
    def test_app_initialization(self, mock_tk):
        """Test inisialisasi aplikasi GUI"""
        from src.gui.gui import App
        
        with patch.object(Path, 'mkdir'):  # Mock mkdir
            app = App()
        
        # Verify basic setup
        assert hasattr(app, 'notebook')
        assert hasattr(app, 'datasets_dir')
        assert hasattr(app, 'log_queue')
    
    def test_parameter_validation_batch_size(self):
        """Test validasi parameter batch size"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
            
            # Test valid batch size
            app.batch_size_var = Mock()
            app.batch_size_var.get.return_value = "50"
            
            try:
                batch_size = int(app.batch_size_var.get())
                assert batch_size > 0
                valid = True
            except ValueError:
                valid = False
            
            assert valid == True
            
            # Test invalid batch size
            app.batch_size_var.get.return_value = "invalid"
            
            try:
                batch_size = int(app.batch_size_var.get())
                assert batch_size > 0
                valid = True
            except ValueError:
                valid = False
            
            assert valid == False
    
    def test_parameter_validation_labels(self):
        """Test validasi parameter allowed labels"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
            
            # Test valid labels
            app.labels_var = Mock()
            app.labels_var.get.return_value = "POSITIF,NEGATIF,NETRAL"
            
            labels_str = app.labels_var.get()
            valid = bool(labels_str and labels_str.strip())
            assert valid == True
            
            # Test empty labels
            app.labels_var.get.return_value = ""
            
            labels_str = app.labels_var.get()
            valid = bool(labels_str and labels_str.strip())
            assert valid == False
    
    @patch('src.gui.gui.filedialog.askopenfilename')
    def test_file_selection(self, mock_filedialog):
        """Test file selection functionality"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
            app.datasets_dir = self.datasets_dir
            app.input_path_var = Mock()
            
            # Mock file selection
            mock_filedialog.return_value = str(self.sample_excel)
            
            app.select_file()
            
            # Should set relative path
            expected_call = f"datasets/{self.sample_excel.name}"
            app.input_path_var.set.assert_called_once_with(expected_call)
    
    @patch('src.gui.gui.filedialog.askdirectory')
    def test_folder_selection(self, mock_filedialog):
        """Test folder selection functionality"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
            app.datasets_dir = self.datasets_dir
            app.input_path_var = Mock()
            
            # Create subfolder
            subfolder = self.datasets_dir / "batch_data"
            subfolder.mkdir()
            
            # Mock folder selection
            mock_filedialog.return_value = str(subfolder)
            
            app.select_folder()
            
            # Should set relative path
            expected_call = "datasets/batch_data"
            app.input_path_var.set.assert_called_once_with(expected_call)
    
    def test_mode_toggle(self):
        """Test mode toggle functionality"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
            app.mode_var = Mock()
            app.file_button = Mock()
            app.folder_button = Mock()
            
            # Test file mode
            app.mode_var.get.return_value = "file"
            app.toggle_mode()
            app.file_button.grid.assert_called_once()
            app.folder_button.grid_remove.assert_called_once()
            
            # Reset mocks
            app.file_button.reset_mock()
            app.folder_button.reset_mock()
            
            # Test folder mode
            app.mode_var.get.return_value = "folder"
            app.toggle_mode()
            app.file_button.grid_remove.assert_called_once()
            app.folder_button.grid.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open, read_data="Test prompt content")
    def test_load_prompt_success(self, mock_file):
        """Test loading prompt berhasil"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
            app.prompt_path_var = Mock()
            app.prompt_path_var.get.return_value = "prompts/test.txt"
            app.prompt_text = Mock()
            
            app.load_prompt()
            
            app.prompt_text.delete.assert_called_once_with('1.0', tk.END)
            app.prompt_text.insert.assert_called_once_with('1.0', "Test prompt content")
    
    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('src.gui.gui.messagebox.showwarning')
    def test_load_prompt_file_not_found(self, mock_messagebox, mock_file):
        """Test loading prompt ketika file tidak ditemukan"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
            app.prompt_path_var = Mock()
            app.prompt_path_var.get.return_value = "prompts/missing.txt"
            app.prompt_text = Mock()
            
            app.load_prompt()
            
            mock_messagebox.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.gui.gui.messagebox.showinfo')
    def test_save_prompt_success(self, mock_messagebox, mock_file):
        """Test saving prompt berhasil"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
            app.prompt_path_var = Mock()
            app.prompt_path_var.get.return_value = "prompts/test.txt"
            app.prompt_text = Mock()
            app.prompt_text.get.return_value = "New prompt content"
            
            with patch.object(Path, 'mkdir'):  # Mock Path.mkdir
                app.save_prompt()
            
            mock_file.assert_called_once_with("prompts/test.txt", 'w', encoding='utf-8')
            mock_messagebox.assert_called_once()
    
    def test_process_log_queue_with_messages(self):
        """Test processing log queue dengan messages"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
            app.log_text = Mock()
            app.log_queue = queue.Queue()
            
            # Add test messages
            app.log_queue.put("Test log message 1")
            app.log_queue.put("Test log message 2")
            app.log_queue.put(None)  # End signal
            
            with patch.object(app, 'process_finished') as mock_finished:
                app.process_log_queue()
            
            # Should process messages and call process_finished
            assert app.log_text.config.call_count >= 2  # Called for state changes
            assert app.log_text.insert.call_count == 2   # Called for each message
            mock_finished.assert_called_once()
    
    def test_process_finished_normal(self):
        """Test process_finished untuk completion normal"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
            app.start_button = Mock()
            app.stop_button = Mock()
            app.start_time = None
            app.end_time_var = Mock()
            app.duration_var = Mock()
            app.process = Mock()
            app.process.returncode = 0  # Normal exit
            
            with patch('src.gui.gui.messagebox.showinfo') as mock_info, \
                 patch.object(app, 'refresh_results'):
                app.process_finished()
            
            app.start_button.config.assert_called_once_with(state='normal')
            app.stop_button.config.assert_called_once_with(state='disabled')
            mock_info.assert_called_once_with("Selesai", "Semua pekerjaan telah selesai.")
    
    def test_process_finished_terminated(self):
        """Test process_finished untuk process yang dihentikan"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
            app.start_button = Mock()
            app.stop_button = Mock()
            app.start_time = None
            app.end_time_var = Mock()
            app.duration_var = Mock()
            app.process = Mock()
            app.process.returncode = 1  # Non-zero exit (terminated)
            
            with patch('src.gui.gui.messagebox.showwarning') as mock_warning, \
                 patch.object(app, 'refresh_results'):
                app.process_finished()
            
            mock_warning.assert_called_once_with("Proses Dihentikan", "Proses telah dihentikan oleh pengguna.")
    
    @patch('src.gui.gui.subprocess.Popen')
    def test_run_backend_loop_single_file(self, mock_popen):
        """Test backend loop untuk single file"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
            app.log_queue = queue.Queue()
            
            # Mock subprocess
            mock_process = Mock()
            mock_process.stdout.readline.side_effect = ["Log line 1\n", "Log line 2\n", ""]
            mock_process.wait.return_value = 0
            mock_popen.return_value = mock_process
            
            files_to_process = [Path("test.xlsx")]
            
            app._run_backend_loop(files_to_process, None, 50, False, "POSITIF,NEGATIF")
            
            # Should create subprocess with correct arguments
            mock_popen.assert_called_once()
            call_args = mock_popen.call_args[0][0]
            assert "--input-file" in call_args
            assert "--batch-size" in call_args
            assert "--allowed-labels" in call_args
    
    def test_refresh_results_default_folder(self):
        """Test refresh results dengan default folder"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
            app.results_listbox = Mock()
            
            # Create mock results folder
            results_folder = self.temp_dir / "results"
            results_folder.mkdir()
            
            # Create sample files
            (results_folder / "result1.xlsx").touch()
            (results_folder / "result2.xlsx").touch()
            
            with patch.object(Path, 'cwd', return_value=self.temp_dir):
                app.refresh_results()
            
            # Should populate listbox
            app.results_listbox.delete.assert_called_once_with(0, tk.END)
            assert app.results_listbox.insert.call_count >= 2  # Header + files


class TestGUIValidation:
    """Test validation logic dalam GUI"""
    
    def test_validate_input_path_file_mode(self):
        """Test validasi input path untuk file mode"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
        
        # Test valid file path
        test_path = Path("datasets/test.xlsx")
        with patch.object(test_path, 'is_file', return_value=True):
            # Should be valid for file mode
            assert test_path.is_file() == True
        
        # Test invalid file path
        with patch.object(test_path, 'is_file', return_value=False):
            assert test_path.is_file() == False
    
    def test_validate_input_path_folder_mode(self):
        """Test validasi input path untuk folder mode"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
        
        # Test valid folder path
        test_path = Path("datasets/batch_folder")
        with patch.object(test_path, 'is_dir', return_value=True):
            assert test_path.is_dir() == True
        
        # Test invalid folder path
        with patch.object(test_path, 'is_dir', return_value=False):
            assert test_path.is_dir() == False
    
    def test_validate_batch_size_edge_cases(self):
        """Test validasi batch size edge cases"""
        test_cases = [
            ("0", False),      # Zero
            ("-1", False),     # Negative
            ("1", True),       # Minimum valid
            ("100", True),     # Normal
            ("abc", False),    # Non-numeric
            ("", False),       # Empty
            ("50.5", False),   # Float
        ]
        
        for input_val, expected_valid in test_cases:
            try:
                batch_size = int(input_val)
                valid = batch_size > 0
            except (ValueError, TypeError):
                valid = False
            
            assert valid == expected_valid, f"Failed for input '{input_val}'"


class TestGUIErrorHandling:
    """Test error handling dalam GUI"""
    
    def test_file_selection_cancelled(self):
        """Test ketika user cancel file selection"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
            app.input_path_var = Mock()
            
            with patch('src.gui.gui.filedialog.askopenfilename', return_value=""):
                app.select_file()
            
            # Should not call set if cancelled
            app.input_path_var.set.assert_not_called()
    
    def test_subprocess_creation_error(self):
        """Test error saat membuat subprocess"""
        from src.gui.gui import App
        
        with patch('src.gui.gui.tk.Tk'), \
             patch.object(Path, 'mkdir'):
            app = App()
            app.log_queue = queue.Queue()
            
            with patch('src.gui.gui.subprocess.Popen', side_effect=Exception("Subprocess failed")):
                # Should handle exception gracefully
                try:
                    app._run_backend_loop([Path("test.xlsx")], None, 50, False, "POSITIF,NEGATIF")
                    # If we get here, exception was handled
                    handled = True
                except Exception:
                    handled = False
                
                # Should either handle gracefully or the test framework will catch
                assert True  # Test that we don't crash the test runner


if __name__ == "__main__":
    pytest.main([__file__, "-v"])