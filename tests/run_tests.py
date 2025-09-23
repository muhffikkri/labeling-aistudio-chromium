#!/usr/bin/env python3
"""
Test runner script untuk menjalankan berbagai jenis tests
"""
import subprocess
import sys
from pathlib import Path
import argparse


def run_command(cmd: list, description: str) -> bool:
    """Run command dan tampilkan hasilnya"""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def run_unit_tests():
    """Jalankan unit tests"""
    cmd = [sys.executable, "-m", "pytest", "-m", "unit", "-v"]
    return run_command(cmd, "Unit Tests")


def run_integration_tests():
    """Jalankan integration tests"""
    cmd = [sys.executable, "-m", "pytest", "-m", "integration", "-v"]
    return run_command(cmd, "Integration Tests")


def run_all_tests():
    """Jalankan semua tests"""
    cmd = [sys.executable, "-m", "pytest", "-v"]
    return run_command(cmd, "All Tests")


def run_with_coverage():
    """Jalankan tests dengan coverage report"""
    cmd = [sys.executable, "-m", "pytest", "--cov=src", "--cov-report=html", "--cov-report=term-missing", "-v"]
    return run_command(cmd, "Tests with Coverage")


def run_specific_file(filename: str):
    """Jalankan tests dari file specific"""
    cmd = [sys.executable, "-m", "pytest", f"tests/{filename}", "-v"]
    return run_command(cmd, f"Tests from {filename}")


def run_gui_tests():
    """Jalankan GUI tests"""
    cmd = [sys.executable, "-m", "pytest", "-m", "gui", "-v"]
    return run_command(cmd, "GUI Tests")


def run_browser_tests():
    """Jalankan browser automation tests"""
    cmd = [sys.executable, "-m", "pytest", "-m", "browser", "-v"]
    return run_command(cmd, "Browser Automation Tests")


def run_fast_tests():
    """Jalankan fast tests (exclude slow tests)"""
    cmd = [sys.executable, "-m", "pytest", "-m", "not slow", "-v"]
    return run_command(cmd, "Fast Tests")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test runner untuk labeling application")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--gui", action="store_true", help="Run GUI tests only")
    parser.add_argument("--browser", action="store_true", help="Run browser tests only")
    parser.add_argument("--fast", action="store_true", help="Run fast tests (exclude slow)")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--file", type=str, help="Run tests from specific file")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest is not installed. Install it with: pip install pytest pytest-cov")
        return 1
    
    results = []
    
    if args.unit:
        results.append(run_unit_tests())
    elif args.integration:
        results.append(run_integration_tests())
    elif args.gui:
        results.append(run_gui_tests())
    elif args.browser:
        results.append(run_browser_tests())
    elif args.fast:
        results.append(run_fast_tests())
    elif args.coverage:
        results.append(run_with_coverage())
    elif args.file:
        results.append(run_specific_file(args.file))
    elif args.all:
        results.append(run_all_tests())
    else:
        # Default: run all tests
        print("🚀 Running All Tests...")
        results.append(run_all_tests())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        return 0
    else:
        print(f"⚠️  Some tests failed. ({passed}/{total} passed)")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)