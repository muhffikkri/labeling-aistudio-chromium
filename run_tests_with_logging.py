#!/usr/bin/env python3
"""
Enhanced test runner dengan logging untuk hasil testing
"""
import subprocess
import sys
import logging
import json
from pathlib import Path
import argparse
from datetime import datetime
import time
import os


class TestLogger:
    """Logger khusus untuk hasil testing"""
    
    def __init__(self, log_dir: Path = None):
        """Initialize test logger"""
        if log_dir is None:
            log_dir = Path("test_logs")
        
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"test_run_{timestamp}.log"
        self.json_file = self.log_dir / f"test_results_{timestamp}.json"
        
        # Setup logging
        self.logger = logging.getLogger("TestRunner")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Console handler  
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Test results storage
        self.test_results = {
            "session_start": datetime.now().isoformat(),
            "session_end": None,
            "total_duration": 0,
            "environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": str(Path.cwd())
            },
            "test_runs": []
        }
        
        self.logger.info("=" * 60)
        self.logger.info("🚀 TEST SESSION STARTED")
        self.logger.info(f"📁 Log file: {self.log_file}")
        self.logger.info(f"📊 Results file: {self.json_file}")
        self.logger.info("=" * 60)
    
    def log_test_run(self, test_type: str, cmd: list, result: subprocess.CompletedProcess, duration: float):
        """Log hasil test run"""
        success = result.returncode == 0
        
        # Log ke console dan file
        status = "✅ PASSED" if success else "❌ FAILED"
        self.logger.info(f"🧪 {test_type}: {status} (Duration: {duration:.2f}s)")
        
        if result.stdout:
            self.logger.info(f"📋 STDOUT:\n{result.stdout}")
        
        if result.stderr:
            self.logger.warning(f"⚠️  STDERR:\n{result.stderr}")
        
        # Store structured results
        test_run_data = {
            "test_type": test_type,
            "command": " ".join(cmd),
            "success": success,
            "return_code": result.returncode,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
            "stdout_lines": len(result.stdout.splitlines()) if result.stdout else 0,
            "stderr_lines": len(result.stderr.splitlines()) if result.stderr else 0,
        }
        
        # Parse pytest output for more details if available
        if result.stdout and "collected" in result.stdout.lower():
            test_run_data.update(self._parse_pytest_output(result.stdout))
        
        self.test_results["test_runs"].append(test_run_data)
        
        return success
    
    def _parse_pytest_output(self, stdout: str) -> dict:
        """Parse pytest output untuk extract test statistics"""
        stats = {
            "tests_collected": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0,
            "warnings": 0
        }
        
        try:
            lines = stdout.splitlines()
            
            # Look for collection info
            for line in lines:
                if "collected" in line and "item" in line:
                    words = line.split()
                    for i, word in enumerate(words):
                        if word.isdigit() and i + 1 < len(words) and "item" in words[i + 1]:
                            stats["tests_collected"] = int(word)
                            break
            
            # Look for summary line
            summary_line = None
            for line in reversed(lines):
                if any(keyword in line for keyword in ["passed", "failed", "error", "skipped"]):
                    summary_line = line
                    break
            
            if summary_line:
                # Parse summary like "1 failed, 9 passed, 1 warning in 0.24s"
                parts = summary_line.split(",")
                for part in parts:
                    part = part.strip()
                    if "passed" in part:
                        stats["tests_passed"] = int(part.split()[0])
                    elif "failed" in part:
                        stats["tests_failed"] = int(part.split()[0])
                    elif "skipped" in part:
                        stats["tests_skipped"] = int(part.split()[0])
                    elif "warning" in part:
                        stats["warnings"] = int(part.split()[0])
        
        except (ValueError, IndexError):
            pass  # If parsing fails, return default stats
        
        return stats
    
    def finalize_session(self):
        """Finalize testing session dan save results"""
        self.test_results["session_end"] = datetime.now().isoformat()
        
        # Calculate total duration
        start_time = datetime.fromisoformat(self.test_results["session_start"])
        end_time = datetime.fromisoformat(self.test_results["session_end"])
        self.test_results["total_duration"] = (end_time - start_time).total_seconds()
        
        # Calculate summary statistics
        total_runs = len(self.test_results["test_runs"])
        successful_runs = sum(1 for run in self.test_results["test_runs"] if run["success"])
        failed_runs = total_runs - successful_runs
        
        self.test_results["summary"] = {
            "total_test_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "success_rate": (successful_runs / total_runs * 100) if total_runs > 0 else 0
        }
        
        # Save JSON results
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        # Log summary
        self.logger.info("=" * 60)
        self.logger.info("📊 TEST SESSION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"⏱️  Total Duration: {self.test_results['total_duration']:.2f}s")
        self.logger.info(f"🧪 Test Runs: {total_runs}")
        self.logger.info(f"✅ Successful: {successful_runs}")
        self.logger.info(f"❌ Failed: {failed_runs}")
        self.logger.info(f"📈 Success Rate: {self.test_results['summary']['success_rate']:.1f}%")
        self.logger.info(f"💾 Results saved to: {self.json_file}")
        self.logger.info("=" * 60)


class EnhancedTestRunner:
    """Enhanced test runner dengan logging capabilities"""
    
    def __init__(self):
        self.test_logger = TestLogger()
    
    def run_command(self, cmd: list, description: str) -> bool:
        """Run command dengan logging"""
        self.test_logger.logger.info(f"🚀 Starting: {description}")
        self.test_logger.logger.info(f"💻 Command: {' '.join(cmd)}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            duration = time.time() - start_time
            
            success = self.test_logger.log_test_run(description, cmd, result, duration)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.test_logger.logger.error(f"❌ Error running {description}: {e}")
            
            # Create dummy result for logging
            dummy_result = subprocess.CompletedProcess(cmd, 1, "", str(e))
            self.test_logger.log_test_run(description, cmd, dummy_result, duration)
            return False
    
    def run_unit_tests(self):
        """Jalankan unit tests"""
        cmd = [sys.executable, "-m", "pytest", "-m", "unit", "-v"]
        return self.run_command(cmd, "Unit Tests")
    
    def run_integration_tests(self):
        """Jalankan integration tests"""
        cmd = [sys.executable, "-m", "pytest", "-m", "integration", "-v"]
        return self.run_command(cmd, "Integration Tests")
    
    def run_all_tests(self):
        """Jalankan semua tests"""
        cmd = [sys.executable, "-m", "pytest", "-v"]
        return self.run_command(cmd, "All Tests")
    
    def run_with_coverage(self):
        """Jalankan tests dengan coverage report"""
        cmd = [sys.executable, "-m", "pytest", "--cov=src", "--cov-report=html", "--cov-report=term-missing", "-v"]
        return self.run_command(cmd, "Tests with Coverage")
    
    def run_specific_file(self, filename: str):
        """Jalankan tests dari file specific"""
        cmd = [sys.executable, "-m", "pytest", f"tests/{filename}", "-v"]
        return self.run_command(cmd, f"Tests from {filename}")
    
    def run_gui_tests(self):
        """Jalankan GUI tests"""
        cmd = [sys.executable, "-m", "pytest", "-m", "gui", "-v"]
        return self.run_command(cmd, "GUI Tests")
    
    def run_browser_tests(self):
        """Jalankan browser automation tests"""
        cmd = [sys.executable, "-m", "pytest", "-m", "browser", "-v"]
        return self.run_command(cmd, "Browser Automation Tests")
    
    def run_fast_tests(self):
        """Jalankan fast tests (exclude slow tests)"""
        cmd = [sys.executable, "-m", "pytest", "-m", "not slow", "-v"]
        return self.run_command(cmd, "Fast Tests")
    
    def run_with_junit_xml(self):
        """Run tests dan generate JUnit XML report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        xml_file = f"test_logs/junit_results_{timestamp}.xml"
        cmd = [sys.executable, "-m", "pytest", f"--junitxml={xml_file}", "-v"]
        success = self.run_command(cmd, "Tests with JUnit XML")
        
        if success:
            self.test_logger.logger.info(f"📄 JUnit XML report: {xml_file}")
        
        return success
    
    def finalize(self):
        """Finalize test session"""
        self.test_logger.finalize_session()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Enhanced test runner dengan logging")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--gui", action="store_true", help="Run GUI tests only")
    parser.add_argument("--browser", action="store_true", help="Run browser tests only")
    parser.add_argument("--fast", action="store_true", help="Run fast tests (exclude slow)")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--junit", action="store_true", help="Generate JUnit XML report")
    parser.add_argument("--file", type=str, help="Run tests from specific file")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest is not installed. Install it with: pip install pytest pytest-cov")
        return 1
    
    runner = EnhancedTestRunner()
    results = []
    
    try:
        if args.unit:
            results.append(runner.run_unit_tests())
        elif args.integration:
            results.append(runner.run_integration_tests())
        elif args.gui:
            results.append(runner.run_gui_tests())
        elif args.browser:
            results.append(runner.run_browser_tests())
        elif args.fast:
            results.append(runner.run_fast_tests())
        elif args.coverage:
            results.append(runner.run_with_coverage())
        elif args.junit:
            results.append(runner.run_with_junit_xml())
        elif args.file:
            results.append(runner.run_specific_file(args.file))
        elif args.all:
            results.append(runner.run_all_tests())
        else:
            # Default: run all tests
            runner.test_logger.logger.info("🚀 Running All Tests (default)...")
            results.append(runner.run_all_tests())
    
    finally:
        # Always finalize the session
        runner.finalize()
    
    # Final exit code
    passed = sum(results)
    total = len(results)
    
    if passed == total and total > 0:
        print(f"\n🎉 All tests passed! ({passed}/{total})")
        return 0
    else:
        print(f"\n⚠️  Some tests failed. ({passed}/{total} passed)")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)