# tests/conftest.py
"""
Pytest configuration dan shared fixtures
"""
import sys
import os
from pathlib import Path
import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch
import logging

# Set TESTING environment variable as early as possible
os.environ["TESTING"] = "1"

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Setup test logging
try:
    from test_logging_config import setup_test_logging
    TEST_LOG_DIR = setup_test_logging()
except ImportError:
    # Fallback if test_logging_config is not available
    TEST_LOG_DIR = Path("test_logs")
    TEST_LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(TEST_LOG_DIR / "pytest_fallback.log"),
            logging.StreamHandler()
        ]
    )

# Import fixtures
from tests.fixtures import (
    test_data_generator,
    mock_browser_response,
    mock_playwright_page,
    test_file_manager,
    sample_excel_data,
    processed_excel_data,
    mixed_status_data,
    temp_datasets_structure,
    mock_log_handler,
    validation_helpers
)


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment untuk setiap test"""
    # Set environment variables untuk testing
    monkeypatch.setenv("TESTING", "1")
    
    # Mock home directory untuk testing
    test_home = Path(tempfile.mkdtemp())
    monkeypatch.setenv("HOME", str(test_home))
    
    # Ensure test_logs directory exists
    TEST_LOG_DIR.mkdir(exist_ok=True)
    
    # Setup test-specific logger
    test_logger = logging.getLogger(f"test_{os.getpid()}")
    test_logger.info(f"🧪 Test environment setup completed")
    
    yield
    
    # Cleanup
    if test_home.exists():
        shutil.rmtree(test_home)


@pytest.fixture
def mock_playwright():
    """Mock playwright untuk browser automation tests"""
    with patch('playwright.async_api.async_playwright') as mock:
        # Setup mock playwright instance
        playwright_mock = Mock()
        context_manager_mock = Mock()
        context_manager_mock.__aenter__ = Mock(return_value=playwright_mock)
        context_manager_mock.__aexit__ = Mock(return_value=None)
        mock.return_value = context_manager_mock
        
        # Setup chromium browser mock
        browser_mock = Mock()
        playwright_mock.chromium.launch.return_value.__aenter__ = Mock(return_value=browser_mock)
        playwright_mock.chromium.launch.return_value.__aexit__ = Mock(return_value=None)
        
        # Setup context mock
        context_mock = Mock()
        browser_mock.new_context.return_value.__aenter__ = Mock(return_value=context_mock)
        browser_mock.new_context.return_value.__aexit__ = Mock(return_value=None)
        
        # Setup page mock
        page_mock = Mock()
        context_mock.new_page.return_value = page_mock
        
        yield {
            'playwright': playwright_mock,
            'browser': browser_mock,
            'context': context_mock,
            'page': page_mock
        }


@pytest.fixture
def mock_subprocess():
    """Mock subprocess untuk testing GUI backend calls"""
    with patch('subprocess.Popen') as mock_popen:
        # Create mock process
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout.readline.return_value = b'Test log line\n'
        mock_process.wait.return_value = 0
        mock_process.poll.return_value = 0
        mock_popen.return_value = mock_process
        
        yield mock_process


@pytest.fixture
def mock_tkinter():
    """Mock tkinter untuk GUI testing tanpa window"""
    with patch('tkinter.Tk') as mock_tk, \
         patch('tkinter.ttk') as mock_ttk, \
         patch('tkinter.filedialog') as mock_filedialog, \
         patch('tkinter.messagebox') as mock_messagebox:
        
        # Setup basic Tk mock
        tk_instance = Mock()
        mock_tk.return_value = tk_instance
        
        yield {
            'tk': tk_instance,
            'ttk': mock_ttk,
            'filedialog': mock_filedialog,
            'messagebox': mock_messagebox
        }


@pytest.fixture
def temp_work_directory():
    """Temporary working directory untuk tests"""
    original_cwd = os.getcwd()
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        os.chdir(temp_dir)
        yield temp_dir
    finally:
        os.chdir(original_cwd)
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


@pytest.fixture
def mock_logger():
    """Mock logger untuk testing"""
    with patch('logging.getLogger') as mock_get_logger:
        logger_mock = Mock()
        mock_get_logger.return_value = logger_mock
        yield logger_mock


@pytest.fixture
def clean_imports():
    """Clean sys.modules setelah test untuk avoid import conflicts"""
    original_modules = sys.modules.copy()
    yield
    
    # Remove any modules yang diimport selama test
    modules_to_remove = []
    for module_name in sys.modules:
        if module_name not in original_modules:
            modules_to_remove.append(module_name)
    
    for module_name in modules_to_remove:
        if module_name in sys.modules:
            del sys.modules[module_name]


# Test markers untuk skip tests conditional
def pytest_runtest_setup(item):
    """Setup hook untuk conditional test skipping"""
    # Skip browser tests jika playwright tidak tersedia
    if item.get_closest_marker("browser"):
        try:
            import playwright
        except ImportError:
            pytest.skip("Playwright not available")
    
    # Skip GUI tests jika tkinter tidak tersedia
    if item.get_closest_marker("gui"):
        try:
            import tkinter
        except ImportError:
            pytest.skip("tkinter not available")
    
    # Skip slow tests jika running dengan -m "not slow"
    if item.get_closest_marker("slow"):
        if item.config.getoption("-m") == "not slow":
            pytest.skip("Slow test skipped")


# Custom assertions
class CustomAssertions:
    """Custom assertion methods untuk testing"""
    
    @staticmethod
    def assert_file_exists(filepath: Path, msg: str = None):
        """Assert bahwa file exists"""
        if not filepath.exists():
            raise AssertionError(msg or f"File {filepath} does not exist")
    
    @staticmethod
    def assert_file_not_empty(filepath: Path, msg: str = None):
        """Assert bahwa file tidak kosong"""
        if not filepath.exists():
            raise AssertionError(f"File {filepath} does not exist")
        if filepath.stat().st_size == 0:
            raise AssertionError(msg or f"File {filepath} is empty")
    
    @staticmethod
    def assert_dataframe_has_columns(df, expected_columns, msg: str = None):
        """Assert bahwa DataFrame has expected columns"""
        missing_columns = set(expected_columns) - set(df.columns)
        if missing_columns:
            raise AssertionError(msg or f"DataFrame missing columns: {missing_columns}")
    
    @staticmethod
    def assert_log_contains(logs, expected_message, level=None, msg: str = None):
        """Assert bahwa logs contain expected message"""
        for log_level, log_message in logs:
            if level and log_level != level:
                continue
            if expected_message in log_message:
                return
        raise AssertionError(msg or f"Log message '{expected_message}' not found")


@pytest.fixture
def custom_assertions():
    """Fixture untuk custom assertions"""
    return CustomAssertions


# Test utilities
class TestUtilities:
    """Utility functions untuk testing"""
    
    @staticmethod
    def wait_for_condition(condition, timeout=5, interval=0.1):
        """Wait for condition dengan timeout"""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition():
                return True
            time.sleep(interval)
        return False
    
    @staticmethod
    def create_test_excel_with_encoding(filepath: Path, data, encoding='utf-8'):
        """Create Excel file dengan specific encoding"""
        import pandas as pd
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            data.to_excel(writer, index=False, sheet_name='Sheet1')
    
    @staticmethod
    def simulate_user_input(inputs: list):
        """Simulate user input untuk interactive tests"""
        input_iterator = iter(inputs)
        return lambda prompt="": next(input_iterator, "")


@pytest.fixture
def test_utilities():
    """Fixture untuk test utilities"""
    return TestUtilities


# Session-scoped fixtures untuk expensive setup
@pytest.fixture(scope="session")
def test_data_cache():
    """Cache untuk test data yang expensive untuk generate"""
    cache = {}
    yield cache
    # Cleanup cache if needed


# Hook untuk test result reporting
def pytest_runtest_logreport(report):
    """Hook untuk custom test reporting"""
    if report.when == "call" and report.outcome == "failed":
        # Add extra information untuk failed tests
        if hasattr(report.longrepr, 'reprcrash'):
            crash = report.longrepr.reprcrash
            print(f"\nTest failed: {report.nodeid}")
            print(f"Location: {crash.path}:{crash.lineno}")


# Configure test collection
def pytest_collection_modifyitems(config, items):
    """Modify test collection untuk add markers"""
    for item in items:
        # Add unit marker untuk test files yang start dengan test_
        if "test_" in item.fspath.basename and not any(
            marker in item.fspath.basename for marker in ["integration", "gui", "browser"]
        ):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker untuk integration test files
        if "integration" in item.fspath.basename:
            item.add_marker(pytest.mark.integration)
        
        # Add gui marker untuk GUI test files
        if "gui" in item.fspath.basename:
            item.add_marker(pytest.mark.gui)
        
        # Add browser marker untuk browser test files
        if "browser" in item.fspath.basename:
            item.add_marker(pytest.mark.browser)


# Fixtures untuk specific components
@pytest.fixture
def validation_config():
    """Configuration untuk validation tests"""
    return {
        'allowed_labels': ['POSITIF', 'NEGATIF', 'NETRAL', 'TIDAK RELEVAN'],
        'batch_size': 50,
        'timeout': 30,
        'max_retries': 3
    }


@pytest.fixture
def browser_config():
    """Configuration untuk browser tests"""
    return {
        'headless': True,
        'timeout': 30000,
        'viewport': {'width': 1280, 'height': 720},
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }