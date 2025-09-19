# tests/fixtures.py
"""
Test fixtures dan helper utilities untuk testing
"""
import sys
from pathlib import Path
import pytest
import pandas as pd
import tempfile
import shutil
from typing import Dict, List, Any
from unittest.mock import Mock, MagicMock
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestDataGenerator:
    """Generator untuk test data"""
    
    @staticmethod
    def create_sample_excel_data(num_rows: int = 10) -> pd.DataFrame:
        """Buat sample data untuk testing Excel files"""
        data = {
            'id': range(1, num_rows + 1),
            'text': [f"Sample text content {i}" for i in range(1, num_rows + 1)],
            'label': ['PENDING'] * num_rows,
            'status': ['UNPROCESSED'] * num_rows,
            'confidence': [0.0] * num_rows,
            'processed_at': [''] * num_rows
        }
        return pd.DataFrame(data)
    
    @staticmethod
    def create_processed_excel_data(num_rows: int = 5) -> pd.DataFrame:
        """Buat sample data yang sudah diproses"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        data = {
            'id': range(1, num_rows + 1),
            'text': [f"Processed text content {i}" for i in range(1, num_rows + 1)],
            'label': ['POSITIF', 'NEGATIF', 'NETRAL', 'POSITIF', 'NEGATIF'][:num_rows],
            'status': ['COMPLETED'] * num_rows,
            'confidence': [0.85, 0.92, 0.78, 0.88, 0.90][:num_rows],
            'processed_at': [timestamp] * num_rows
        }
        return pd.DataFrame(data)
    
    @staticmethod
    def create_mixed_status_data(num_rows: int = 10) -> pd.DataFrame:
        """Buat data dengan status mixed"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        data = {
            'id': range(1, num_rows + 1),
            'text': [f"Mixed status text {i}" for i in range(1, num_rows + 1)],
            'label': (['POSITIF', 'NEGATIF'] * 5)[:num_rows],
            'status': (['COMPLETED', 'FAILED', 'PENDING'] * 4)[:num_rows],
            'confidence': ([0.85, 0.0, 0.0] * 4)[:num_rows],
            'processed_at': ([timestamp, '', ''] * 4)[:num_rows]
        }
        return pd.DataFrame(data)


class MockBrowserResponse:
    """Mock response dari browser automation"""
    
    def __init__(self, success: bool = True, content: str = None):
        self.success = success
        self.content = content or self._generate_default_content()
    
    def _generate_default_content(self) -> str:
        """Generate default response content"""
        return """
        <div class="response-container">
            <p>POSITIF</p>
            <div class="reasoning">
                Text ini mengandung sentimen positif karena...
            </div>
        </div>
        """
    
    @classmethod
    def create_success_response(cls, label: str = "POSITIF") -> 'MockBrowserResponse':
        """Create successful response"""
        content = f"""
        <div class="response-container">
            <p>{label}</p>
            <div class="reasoning">
                Text analysis completed successfully.
            </div>
        </div>
        """
        return cls(success=True, content=content)
    
    @classmethod
    def create_failure_response(cls) -> 'MockBrowserResponse':
        """Create failed response"""
        return cls(success=False, content="")


class MockPlaywrightPage:
    """Mock Playwright page object"""
    
    def __init__(self):
        self.url = None
        self.content = ""
        self.is_closed = False
        self.locators = {}
        self.wait_results = []
    
    async def goto(self, url: str, **kwargs):
        """Mock goto method"""
        self.url = url
        return Mock(ok=True)
    
    async def wait_for_selector(self, selector: str, **kwargs):
        """Mock wait_for_selector"""
        return Mock()
    
    async def fill(self, selector: str, value: str):
        """Mock fill method"""
        pass
    
    async def click(self, selector: str, **kwargs):
        """Mock click method"""
        pass
    
    async def content(self):
        """Mock content method"""
        return self.content
    
    def locator(self, selector: str):
        """Mock locator method"""
        mock_locator = Mock()
        mock_locator.inner_text = Mock(return_value="Mocked text")
        mock_locator.is_visible = Mock(return_value=True)
        return mock_locator
    
    async def close(self):
        """Mock close method"""
        self.is_closed = True


class MockPlaywrightContext:
    """Mock Playwright browser context"""
    
    def __init__(self):
        self.pages = []
        self.is_closed = False
    
    async def new_page(self):
        """Mock new_page method"""
        page = MockPlaywrightPage()
        self.pages.append(page)
        return page
    
    async def close(self):
        """Mock close method"""
        self.is_closed = True
        for page in self.pages:
            await page.close()


class MockPlaywrightBrowser:
    """Mock Playwright browser"""
    
    def __init__(self):
        self.contexts = []
        self.is_closed = False
    
    async def new_context(self, **kwargs):
        """Mock new_context method"""
        context = MockPlaywrightContext()
        self.contexts.append(context)
        return context
    
    async def close(self):
        """Mock close method"""
        self.is_closed = True
        for context in self.contexts:
            await context.close()


class TestFileManager:
    """Manager untuk temporary test files"""
    
    def __init__(self):
        self.temp_dir = None
        self.created_files = []
    
    def setup_temp_directory(self) -> Path:
        """Setup temporary directory untuk tests"""
        self.temp_dir = Path(tempfile.mkdtemp())
        return self.temp_dir
    
    def create_excel_file(self, filename: str, data: pd.DataFrame) -> Path:
        """Buat Excel file untuk testing"""
        if not self.temp_dir:
            self.setup_temp_directory()
        
        filepath = self.temp_dir / filename
        data.to_excel(filepath, index=False)
        self.created_files.append(filepath)
        return filepath
    
    def create_csv_file(self, filename: str, data: pd.DataFrame) -> Path:
        """Buat CSV file untuk testing"""
        if not self.temp_dir:
            self.setup_temp_directory()
        
        filepath = self.temp_dir / filename
        data.to_csv(filepath, index=False)
        self.created_files.append(filepath)
        return filepath
    
    def create_text_file(self, filename: str, content: str) -> Path:
        """Buat text file untuk testing"""
        if not self.temp_dir:
            self.setup_temp_directory()
        
        filepath = self.temp_dir / filename
        filepath.write_text(content, encoding='utf-8')
        self.created_files.append(filepath)
        return filepath
    
    def create_directory_structure(self, structure: Dict[str, Any]) -> Path:
        """Buat struktur directory untuk testing
        
        Args:
            structure: Dict dengan struktur folder/file
            Contoh: {
                'folder1': {
                    'file1.txt': 'content1',
                    'subfolder': {
                        'file2.txt': 'content2'
                    }
                }
            }
        """
        if not self.temp_dir:
            self.setup_temp_directory()
        
        self._create_structure_recursive(self.temp_dir, structure)
        return self.temp_dir
    
    def _create_structure_recursive(self, base_path: Path, structure: Dict[str, Any]):
        """Helper untuk membuat struktur secara recursive"""
        for name, content in structure.items():
            path = base_path / name
            
            if isinstance(content, dict):
                # It's a directory
                path.mkdir(exist_ok=True)
                self._create_structure_recursive(path, content)
            else:
                # It's a file
                if isinstance(content, pd.DataFrame):
                    # DataFrame to Excel
                    content.to_excel(path, index=False)
                else:
                    # String content
                    path.write_text(str(content), encoding='utf-8')
                self.created_files.append(path)
    
    def cleanup(self):
        """Cleanup temporary files dan directories"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.created_files.clear()


# Pytest fixtures
@pytest.fixture
def test_data_generator():
    """Fixture untuk TestDataGenerator"""
    return TestDataGenerator()


@pytest.fixture
def mock_browser_response():
    """Fixture untuk MockBrowserResponse"""
    return MockBrowserResponse.create_success_response()


@pytest.fixture
def mock_playwright_page():
    """Fixture untuk MockPlaywrightPage"""
    return MockPlaywrightPage()


@pytest.fixture
def test_file_manager():
    """Fixture untuk TestFileManager"""
    manager = TestFileManager()
    manager.setup_temp_directory()
    
    yield manager
    
    # Cleanup after test
    manager.cleanup()


@pytest.fixture
def sample_excel_data():
    """Fixture untuk sample Excel data"""
    return TestDataGenerator.create_sample_excel_data()


@pytest.fixture
def processed_excel_data():
    """Fixture untuk processed Excel data"""
    return TestDataGenerator.create_processed_excel_data()


@pytest.fixture
def mixed_status_data():
    """Fixture untuk mixed status data"""
    return TestDataGenerator.create_mixed_status_data()


@pytest.fixture
def temp_datasets_structure(test_file_manager):
    """Fixture untuk struktur datasets lengkap"""
    structure = {
        'datasets': {
            'sample.xlsx': TestDataGenerator.create_sample_excel_data(),
            'processed.xlsx': TestDataGenerator.create_processed_excel_data(),
            'batch_folder': {
                'file1.xlsx': TestDataGenerator.create_sample_excel_data(5),
                'file2.xlsx': TestDataGenerator.create_sample_excel_data(7),
                'file3.csv': TestDataGenerator.create_sample_excel_data(3)
            }
        },
        'prompts': {
            'test_prompt.txt': 'Test prompt content for analysis'
        },
        'results': {},
        'logs': {}
    }
    
    return test_file_manager.create_directory_structure(structure)


class MockLogHandler:
    """Mock log handler untuk testing logging functionality"""
    
    def __init__(self):
        self.logs = []
    
    def info(self, msg: str):
        """Mock info logging"""
        self.logs.append(('INFO', msg))
    
    def warning(self, msg: str):
        """Mock warning logging"""
        self.logs.append(('WARNING', msg))
    
    def error(self, msg: str):
        """Mock error logging"""
        self.logs.append(('ERROR', msg))
    
    def debug(self, msg: str):
        """Mock debug logging"""
        self.logs.append(('DEBUG', msg))
    
    def get_logs_by_level(self, level: str) -> List[str]:
        """Get logs by level"""
        return [msg for lvl, msg in self.logs if lvl == level]
    
    def clear(self):
        """Clear all logs"""
        self.logs.clear()


@pytest.fixture
def mock_log_handler():
    """Fixture untuk MockLogHandler"""
    return MockLogHandler()


class ValidationTestHelpers:
    """Helper methods untuk validation testing"""
    
    @staticmethod
    def create_valid_response_content(label: str = "POSITIF") -> str:
        """Create valid HTML response content"""
        return f"""
        <div class="response-container">
            <div class="model-response">
                <p>{label}</p>
                <div class="reasoning">
                    Analysis completed with high confidence.
                </div>
            </div>
        </div>
        """
    
    @staticmethod
    def create_invalid_response_content() -> str:
        """Create invalid HTML response content"""
        return """
        <div class="response-container">
            <div class="error-message">
                Unable to process the request.
            </div>
        </div>
        """
    
    @staticmethod
    def create_malformed_response() -> str:
        """Create malformed HTML response"""
        return "<div incomplete response"
    
    @staticmethod
    def create_response_with_multiple_labels() -> str:
        """Create response with multiple possible labels"""
        return """
        <div class="response-container">
            <p>POSITIF</p>
            <p>Confidence: High</p>
            <div class="alternatives">
                <p>Alternative: NETRAL</p>
            </div>
        </div>
        """


@pytest.fixture
def validation_helpers():
    """Fixture untuk ValidationTestHelpers"""
    return ValidationTestHelpers()


# Custom pytest markers untuk kategorisasi tests
pytest_plugins = []

# Tambahkan custom markers
def pytest_configure(config):
    """Configure pytest dengan custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running test"
    )
    config.addinivalue_line(
        "markers", "browser: mark test as browser automation test"
    )
    config.addinivalue_line(
        "markers", "gui: mark test as GUI test"
    )