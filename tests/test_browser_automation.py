# tests/test_browser_automation.py
import sys
from pathlib import Path
import pytest
import tempfile
import shutil
from unittest.mock import patch, Mock, MagicMock, call

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.core_logic.browser_automation import Automation


class TestBrowserAutomation:
    """Test suite untuk Automation class dengan mocked Playwright"""
    
    def setup_method(self):
        """Setup untuk setiap test method"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.log_folder = self.temp_dir / "logs"
        self.log_folder.mkdir(exist_ok=True)
        self.user_data_dir = str(self.temp_dir / "browser_data")
        
    def teardown_method(self):
        """Cleanup setelah setiap test method"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_mock_playwright(self):
        """Helper untuk membuat mock Playwright objects"""
        mock_playwright = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        # Setup mock chain
        mock_playwright.chromium.launch_persistent_context.return_value = mock_context
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_context.pages = []  # Empty pages initially
        
        return mock_playwright, mock_browser, mock_context, mock_page
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_init_success_persistent_context(self, mock_sync_playwright):
        """Test inisialisasi berhasil dengan persistent context"""
        mock_playwright, mock_browser, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        automation = Automation(self.user_data_dir, self.log_folder)
        
        # Verify playwright setup
        mock_sync_playwright.return_value.start.assert_called_once()
        mock_playwright.chromium.launch_persistent_context.assert_called_once()
        
        # Verify automation attributes
        assert automation.playwright == mock_playwright
        assert automation.context == mock_context
        assert automation.page == mock_page
        
        # Verify page setup
        mock_page.set_default_timeout.assert_called_once_with(60000)
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_init_fallback_to_regular_browser(self, mock_sync_playwright):
        """Test fallback ke regular browser saat persistent context gagal"""
        mock_playwright, mock_browser, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        # Make persistent context fail
        mock_playwright.chromium.launch_persistent_context.side_effect = Exception("Persistent context failed")
        
        automation = Automation(self.user_data_dir, self.log_folder)
        
        # Should fallback to regular browser
        mock_playwright.chromium.launch.assert_called_once()
        mock_browser.new_context.assert_called_once()
        assert automation.browser == mock_browser
        assert automation.context == mock_context
        assert automation.page == mock_page
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_init_fallback_to_headless(self, mock_sync_playwright):
        """Test fallback ke headless browser"""
        mock_playwright, mock_browser, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        # Make both persistent and regular context fail
        mock_playwright.chromium.launch_persistent_context.side_effect = Exception("Persistent failed")
        mock_playwright.chromium.launch.side_effect = [Exception("Regular failed"), mock_browser]
        
        automation = Automation(self.user_data_dir, self.log_folder)
        
        # Should try multiple times and eventually succeed with headless
        assert mock_playwright.chromium.launch.call_count == 2
        headless_call = mock_playwright.chromium.launch.call_args_list[1]
        assert headless_call[1]['headless'] == True
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_init_total_failure(self, mock_sync_playwright):
        """Test ketika semua metode browser launch gagal"""
        mock_playwright, _, _, _ = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        # Make all launch methods fail
        mock_playwright.chromium.launch_persistent_context.side_effect = Exception("Persistent failed")
        mock_playwright.chromium.launch.side_effect = Exception("All launch failed")
        
        with pytest.raises(RuntimeError, match="Gagal meluncurkan browser setelah mencoba semua metode fallback"):
            Automation(self.user_data_dir, self.log_folder)
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_apply_stealth_techniques(self, mock_sync_playwright):
        """Test penerapan stealth techniques"""
        mock_playwright, _, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        automation = Automation(self.user_data_dir, self.log_folder)
        automation._apply_stealth_techniques()
        
        # Should call page.evaluate with stealth script
        mock_page.evaluate.assert_called_once()
        stealth_script = mock_page.evaluate.call_args[0][0]
        assert "navigator.webdriver" in stealth_script
        assert "window.chrome" in stealth_script
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_start_session_success(self, mock_sync_playwright):
        """Test start_session berhasil"""
        mock_playwright, _, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        # Mock page URL check
        mock_page.url = "https://example.com"
        
        # Mock input locator
        mock_locator = Mock()
        mock_page.locator.return_value = mock_locator
        
        automation = Automation(self.user_data_dir, self.log_folder)
        automation.start_session("https://aistudio.google.com/")
        
        # Should navigate to URL
        mock_page.goto.assert_called_once_with("https://aistudio.google.com/", wait_until="domcontentloaded", timeout=90000)
        
        # Should wait for input element
        mock_page.locator.assert_called_with('ms-chunk-input textarea')
        mock_locator.wait_for.assert_called_once_with(state="visible", timeout=180000)
        
        # Should take screenshot
        mock_page.screenshot.assert_called()
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_start_session_timeout(self, mock_sync_playwright):
        """Test start_session timeout"""
        mock_playwright, _, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        mock_page.url = "https://example.com"
        
        # Mock locator to timeout
        mock_locator = Mock()
        mock_locator.wait_for.side_effect = Exception("Timeout waiting for element")
        mock_page.locator.return_value = mock_locator
        
        automation = Automation(self.user_data_dir, self.log_folder)
        
        with pytest.raises(TimeoutError, match="Gagal memulai sesi"):
            automation.start_session("https://aistudio.google.com/")
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_get_raw_response_for_batch_success(self, mock_sync_playwright):
        """Test get_raw_response_for_batch berhasil"""
        mock_playwright, _, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        automation = Automation(self.user_data_dir, self.log_folder)
        
        # Mock wait for generation and extract response
        automation._wait_for_generation_to_complete = Mock(return_value=True)
        automation._extract_response_text = Mock(return_value="POSITIF - Respons berhasil")
        
        result = automation.get_raw_response_for_batch("Test prompt")
        
        # Should fill and click
        mock_page.fill.assert_called_once_with('ms-chunk-input textarea', "Test prompt")
        mock_page.click.assert_called_once_with('footer button[aria-label="Run"]')
        
        # Should wait and extract
        automation._wait_for_generation_to_complete.assert_called_once()
        automation._extract_response_text.assert_called_once()
        
        assert result == "POSITIF - Respons berhasil"
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_get_raw_response_for_batch_with_retries(self, mock_sync_playwright):
        """Test get_raw_response_for_batch dengan retry mechanism"""
        mock_playwright, _, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        automation = Automation(self.user_data_dir, self.log_folder)
        
        # Mock methods
        automation._wait_for_generation_to_complete = Mock(side_effect=[False, False, True])
        automation._extract_response_text = Mock(return_value="POSITIF - Berhasil setelah retry")
        
        with patch('time.sleep'):  # Mock sleep untuk speed up test
            result = automation.get_raw_response_for_batch("Test prompt")
        
        # Should try 3 times
        assert automation._wait_for_generation_to_complete.call_count == 3
        assert mock_page.reload.call_count == 2  # 2 retries
        assert result == "POSITIF - Berhasil setelah retry"
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_get_raw_response_for_batch_all_retries_failed(self, mock_sync_playwright):
        """Test get_raw_response_for_batch ketika semua retry gagal"""
        mock_playwright, _, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        automation = Automation(self.user_data_dir, self.log_folder)
        
        # Mock semua attempt gagal
        automation._wait_for_generation_to_complete = Mock(return_value=False)
        
        with patch('time.sleep'):
            result = automation.get_raw_response_for_batch("Test prompt")
        
        assert result is None
        assert automation._wait_for_generation_to_complete.call_count == 3  # Max retries
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_wait_for_generation_to_complete_success(self, mock_sync_playwright):
        """Test wait_for_generation_to_complete berhasil"""
        mock_playwright, _, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        automation = Automation(self.user_data_dir, self.log_folder)
        
        # Mock stop button behavior
        mock_locator = Mock()
        mock_locator.count.side_effect = [1, 1, 0]  # Initially present, then disappears
        mock_page.locator.return_value = mock_locator
        
        with patch('time.time', side_effect=[0, 5, 10]), \
             patch('time.sleep'):
            result = automation._wait_for_generation_to_complete()
        
        assert result == True
        mock_page.locator.assert_called_with('button:has-text("Stop")')
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_wait_for_generation_to_complete_timeout(self, mock_sync_playwright):
        """Test wait_for_generation_to_complete timeout"""
        mock_playwright, _, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        automation = Automation(self.user_data_dir, self.log_folder)
        
        # Mock stop button to never disappear
        mock_locator = Mock()
        mock_locator.count.return_value = 1  # Always present
        mock_page.locator.return_value = mock_locator
        
        with patch('time.time', side_effect=range(0, 300, 5)), \
             patch('time.sleep'):
            result = automation._wait_for_generation_to_complete()
        
        assert result == False
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_extract_response_text_with_container(self, mock_sync_playwright):
        """Test extract_response_text dengan container yang ditemukan"""
        mock_playwright, _, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        automation = Automation(self.user_data_dir, self.log_folder)
        
        # Mock successful extraction
        mock_element = Mock()
        mock_element.evaluate.return_value = "POSITIF - Extracted text"
        mock_page.query_selector.side_effect = [mock_element, None]  # First selector succeeds
        
        result = automation._extract_response_text()
        
        assert result == "POSITIF - Extracted text"
        mock_page.query_selector.assert_called()
        mock_element.evaluate.assert_called_once()
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_extract_response_text_fallback_to_body(self, mock_sync_playwright):
        """Test extract_response_text fallback ke body"""
        mock_playwright, _, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        automation = Automation(self.user_data_dir, self.log_folder)
        
        # Mock containers not found, but body succeeds
        mock_body_element = Mock()
        mock_body_element.evaluate.return_value = "POSITIF - Body extracted text"
        mock_page.query_selector.side_effect = [None, None, mock_body_element]  # Only body succeeds
        
        result = automation._extract_response_text()
        
        assert result == "POSITIF - Body extracted text"
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_extract_response_text_all_methods_fail(self, mock_sync_playwright):
        """Test extract_response_text ketika semua metode gagal"""
        mock_playwright, _, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        automation = Automation(self.user_data_dir, self.log_folder)
        
        # Mock all extractions fail
        mock_page.query_selector.return_value = None
        
        result = automation._extract_response_text()
        
        assert result is None
        mock_page.screenshot.assert_called_once()  # Should take error screenshot
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_clear_chat_history_success(self, mock_sync_playwright):
        """Test clear_chat_history berhasil"""
        mock_playwright, _, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        automation = Automation(self.user_data_dir, self.log_folder)
        
        # Mock successful clear
        mock_locator = Mock()
        mock_page.locator.return_value = mock_locator
        
        with patch('time.sleep'):
            automation.clear_chat_history()
        
        # Should click chat nav and wait for textarea
        chat_click_call = call('a.nav-item:has-text("Chat")')
        textarea_call = call('ms-chunk-input textarea')
        
        mock_page.locator.assert_has_calls([chat_click_call, textarea_call])
        mock_locator.click.assert_called_once()
        mock_locator.wait_for.assert_called_once_with(state="visible", timeout=60000)
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_clear_chat_history_fallback_to_reload(self, mock_sync_playwright):
        """Test clear_chat_history fallback ke reload"""
        mock_playwright, _, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        automation = Automation(self.user_data_dir, self.log_folder)
        
        # Mock click to fail
        mock_locator = Mock()
        mock_locator.click.side_effect = Exception("Click failed")
        mock_page.locator.return_value = mock_locator
        
        with patch('time.sleep'):
            automation.clear_chat_history()
        
        # Should fallback to reload
        mock_page.reload.assert_called_once_with(wait_until="domcontentloaded")
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_close_session(self, mock_sync_playwright):
        """Test close_session cleanup"""
        mock_playwright, mock_browser, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        automation = Automation(self.user_data_dir, self.log_folder)
        automation.browser = mock_browser  # Set browser for regular mode test
        
        automation.close_session()
        
        # Should close context, browser, and playwright
        mock_context.close.assert_called_once()
        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()
    
    @patch('src.core_logic.browser_automation.sync_playwright')
    def test_close_session_with_errors(self, mock_sync_playwright):
        """Test close_session dengan error handling"""
        mock_playwright, _, mock_context, mock_page = self.create_mock_playwright()
        mock_sync_playwright.return_value.start.return_value = mock_playwright
        
        automation = Automation(self.user_data_dir, self.log_folder)
        
        # Mock context.close to fail
        mock_context.close.side_effect = Exception("Close failed")
        
        # Should not raise exception
        with patch('logging.warning'):
            automation.close_session()
        
        # Playwright stop should still be called
        mock_playwright.stop.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])