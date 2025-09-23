# test_logging_config.py
"""
Konfigurasi logging untuk test suite
"""
import logging
import logging.config
from pathlib import Path
from datetime import datetime


def setup_test_logging(log_dir: Path = None, log_level: str = "INFO") -> Path:
    """
    Setup comprehensive logging untuk test suite
    
    Args:
        log_dir: Directory untuk menyimpan log files (default: test_logs)
        log_level: Level logging (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Path to log directory
    """
    if log_dir is None:
        log_dir = Path("test_logs")
    
    # Create log directory
    log_dir.mkdir(exist_ok=True)
    
    # Create timestamped log files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    log_files = {
        'main': log_dir / f"pytest_main_{timestamp}.log",
        'debug': log_dir / f"pytest_debug_{timestamp}.log",
        'errors': log_dir / f"pytest_errors_{timestamp}.log"
    }
    
    # Logging configuration
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(levelname)s - %(message)s'
            },
            'json': {
                'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
                'datefmt': '%Y-%m-%dT%H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            },
            'main_file': {
                'class': 'logging.FileHandler',
                'level': log_level,
                'formatter': 'detailed',
                'filename': str(log_files['main']),
                'mode': 'w',
                'encoding': 'utf-8'
            },
            'debug_file': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': str(log_files['debug']),
                'mode': 'w',
                'encoding': 'utf-8'
            },
            'error_file': {
                'class': 'logging.FileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': str(log_files['errors']),
                'mode': 'w',
                'encoding': 'utf-8'
            }
        },
        'loggers': {
            # Root logger
            '': {
                'level': 'DEBUG',
                'handlers': ['console', 'main_file', 'debug_file', 'error_file']
            },
            # Pytest specific
            'pytest': {
                'level': 'DEBUG',
                'handlers': ['main_file', 'debug_file'],
                'propagate': False
            },
            # Test modules
            'tests': {
                'level': 'DEBUG',
                'handlers': ['main_file', 'debug_file'],
                'propagate': False
            },
            # Application modules
            'src': {
                'level': 'DEBUG',
                'handlers': ['main_file', 'debug_file', 'error_file'],
                'propagate': False
            }
        }
    }
    
    # Apply configuration
    logging.config.dictConfig(logging_config)
    
    # Log session start
    logger = logging.getLogger('test_session')
    logger.info("=" * 80)
    logger.info("🚀 TEST LOGGING SESSION STARTED")
    logger.info(f"📁 Log directory: {log_dir.absolute()}")
    logger.info(f"📋 Main log: {log_files['main']}")
    logger.info(f"🐛 Debug log: {log_files['debug']}")
    logger.info(f"❌ Error log: {log_files['errors']}")
    logger.info(f"🔧 Log level: {log_level}")
    logger.info("=" * 80)
    
    return log_dir


def create_test_log_summary(log_dir: Path, session_info: dict = None):
    """
    Create summary file untuk test session
    
    Args:
        log_dir: Directory containing log files
        session_info: Additional session information
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = log_dir / f"session_summary_{timestamp}.md"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Test Session Summary\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if session_info:
            f.write("## Session Information\n\n")
            for key, value in session_info.items():
                f.write(f"- **{key.title()}**: {value}\n")
            f.write("\n")
        
        f.write("## Log Files\n\n")
        
        # List all log files in the directory
        log_files = sorted(log_dir.glob("*.log"))
        for log_file in log_files:
            file_size = log_file.stat().st_size
            f.write(f"- **{log_file.name}**: {file_size:,} bytes\n")
        
        f.write("\n## Report Files\n\n")
        
        # List report files
        report_files = []
        report_files.extend(log_dir.glob("*.xml"))  # JUnit XML
        report_files.extend(log_dir.glob("*.json")) # JSON results
        report_files.extend(log_dir.glob("*.csv"))  # CSV exports
        
        if (log_dir / "htmlcov").exists():
            report_files.append(log_dir / "htmlcov" / "index.html")
        
        for report_file in sorted(report_files):
            if report_file.exists():
                file_size = report_file.stat().st_size
                f.write(f"- **{report_file.name}**: {file_size:,} bytes\n")
        
        f.write("\n## Quick Access Commands\n\n")
        f.write("```bash\n")
        f.write(f"# View recent test results\n")
        f.write(f"python analyze_test_logs.py --recent 5\n\n")
        f.write(f"# Show test statistics\n")
        f.write(f"python analyze_test_logs.py --stats\n\n")
        f.write(f"# Analyze failures\n")
        f.write(f"python analyze_test_logs.py --failures\n\n")
        f.write(f"# View coverage report\n")
        f.write(f"open {log_dir}/htmlcov/index.html\n")
        f.write("```\n")
    
    logger = logging.getLogger('test_session')
    logger.info(f"📄 Session summary created: {summary_file}")
    
    return summary_file


# Pytest plugin untuk automatic logging
def pytest_configure(config):
    """Pytest hook untuk setup logging"""
    # Setup test logging when pytest starts
    log_dir = setup_test_logging()
    
    # Store log directory in config for later use
    config._test_log_dir = log_dir


def pytest_sessionstart(session):
    """Pytest hook pada session start"""
    logger = logging.getLogger('pytest_session')
    logger.info("🧪 Pytest session started")
    logger.info(f"📊 Test collection starting...")


def pytest_sessionfinish(session, exitstatus):
    """Pytest hook pada session finish"""
    logger = logging.getLogger('pytest_session')
    
    # Create session summary
    session_info = {
        'exit_status': exitstatus,
        'tests_collected': len(session.items) if hasattr(session, 'items') else 0,
        'python_version': session.config.getoption('--version', default='unknown'),
        'pytest_args': ' '.join(session.config.args)
    }
    
    log_dir = getattr(session.config, '_test_log_dir', Path('test_logs'))
    summary_file = create_test_log_summary(log_dir, session_info)
    
    logger.info("🏁 Pytest session finished")
    logger.info(f"📊 Exit status: {exitstatus}")
    logger.info(f"📄 Summary: {summary_file}")


def pytest_runtest_logstart(nodeid, location):
    """Log saat test mulai dijalankan"""
    logger = logging.getLogger('pytest_test')
    logger.debug(f"▶️  Starting test: {nodeid}")


def pytest_runtest_logfinish(nodeid, location):
    """Log saat test selesai"""
    logger = logging.getLogger('pytest_test')
    logger.debug(f"⏹️  Finished test: {nodeid}")


def pytest_runtest_logreport(report):
    """Log hasil test"""
    logger = logging.getLogger('pytest_result')
    
    if report.when == 'call':
        if report.outcome == 'passed':
            logger.info(f"✅ PASSED: {report.nodeid} ({report.duration:.3f}s)")
        elif report.outcome == 'failed':
            logger.error(f"❌ FAILED: {report.nodeid} ({report.duration:.3f}s)")
            if hasattr(report, 'longrepr') and report.longrepr:
                logger.error(f"Error details: {str(report.longrepr)}")
        elif report.outcome == 'skipped':
            logger.warning(f"⏭️  SKIPPED: {report.nodeid}")


if __name__ == "__main__":
    # Test the logging configuration
    log_dir = setup_test_logging(log_level="DEBUG")
    
    # Test different log levels
    logger = logging.getLogger('test_demo')
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print(f"✅ Test logging configured successfully!")
    print(f"📁 Logs saved to: {log_dir.absolute()}")