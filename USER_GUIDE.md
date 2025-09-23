# 📖 User Guide - AI Studio Auto-Labeling System

## 🎯 Overview

This comprehensive guide covers everything you need to know about running, debugging, and testing the AI Studio Auto-Labeling System.

---

## 🚀 Running the Application

### Quick Start

#### Prerequisites

- Python 3.8+ installed and accessible
- Virtual environment activated
- Input data file in Excel/CSV format
- Customized prompt file

#### Basic Command Structure

All commands run from the **project root directory**:

```bash
python src/main.py [ARGUMENTS]
```

### Command-Line Arguments

| Argument        | Description                                | Required | Default              |
| --------------- | ------------------------------------------ | -------- | -------------------- |
| `--input-file`  | Path to dataset file in `datasets/` folder | ✅ Yes   | -                    |
| `--output-file` | Path for output results                    | ❌ No    | Auto-generated       |
| `--prompt-file` | Path to prompt file                        | ❌ No    | `prompts/prompt.txt` |
| `--batch-size`  | Rows processed per batch                   | ❌ No    | 50                   |
| `--debug`       | Debug mode (processes only one batch)      | ❌ No    | -                    |

### Usage Examples

#### 1. Standard Processing

```bash
python src/main.py --input-file "datasets/my_data.xlsx"
```

#### 2. Custom Batch Size

```bash
python src/main.py --input-file "datasets/my_data.xlsx" --batch-size 25
```

#### 3. Debug Mode

```bash
python src/main.py --input-file "datasets/my_data.xlsx" --debug
```

#### 4. Custom Output Path

```bash
python src/main.py --input-file "datasets/my_data.xlsx" --output-file "results/custom_output.csv"
```

### GUI Interface

Launch the graphical interface:

```bash
python src/gui.py
```

**GUI Features:**

- File selection dialogs
- Real-time progress monitoring
- Settings configuration
- Log viewing capabilities

---

## 🔧 Debugging Guide

### Common Issues & Solutions

#### 1. Browser Automation Issues

**Problem**: Browser fails to launch or times out

```
ERROR: Failed to start browser session due to timeout
```

**Solutions:**

- Check Chrome/Chromium installation
- Verify internet connectivity
- Clear browser data: delete `browser_data/` folder
- Try headless mode or different browser settings

#### 2. File Processing Errors

**Problem**: Excel/CSV file cannot be read

```
ERROR: Could not read the input file
```

**Solutions:**

- Validate file format with: `python tools/validate_excel.py datasets/your_file.xlsx`
- Fix file structure: `python tools/fix_excel_structure.py datasets/your_file.xlsx`
- Check file permissions and encoding

#### 3. AI Studio Connection Issues

**Problem**: Cannot connect to Google AI Studio

```
ERROR: AI Studio interface not accessible
```

**Solutions:**

- Verify Google account login status
- Check AI Studio service availability
- Review browser session state
- Clear browser cache and cookies

#### 4. Quota/Rate Limiting

**Problem**: API quota exceeded

```
WARNING: Request rate exceeds quota limit
```

**Solutions:**

- Monitor request statistics in logs
- Reduce batch size: `--batch-size 10`
- Add delays between requests
- Check quota usage in Google AI Studio

#### 5. Memory Issues

**Problem**: Out of memory during processing

```
ERROR: Memory allocation failed
```

**Solutions:**

- Reduce batch size significantly
- Process data in smaller chunks
- Close unnecessary applications
- Check available system memory

### Debug Features

#### 1. Debug Mode

Enable single-batch processing for testing:

```bash
python src/main.py --input-file "datasets/test.xlsx" --debug
```

#### 2. Log Analysis

Check session logs in `logs/` folder:

- `session_YYYYMMDD_HHMMSS/` - Detailed execution logs
- Screenshots for error diagnosis
- Raw AI responses for validation issues

#### 3. Metrics Recovery

If metrics are corrupted:

```bash
python recover_metrics.py
```

#### 4. File Structure Validation

Validate and fix data files:

```bash
# Validate structure
python tools/validate_excel.py datasets/your_file.xlsx

# Fix structure issues
python tools/fix_excel_structure.py datasets/your_file.xlsx
```

### Performance Optimization

#### 1. Batch Size Tuning

- **Large datasets (>1000 rows)**: Start with batch_size=20-30
- **Small datasets (<500 rows)**: Use batch_size=50-100
- **Rate limiting**: Reduce to batch_size=5-10

#### 2. Resource Monitoring

- Monitor request rates in logs
- Watch memory usage during processing
- Check disk space for logs and outputs

---

## 🧪 Testing Guide

### Test Suite Overview

The system includes **90+ comprehensive test cases** covering:

- Unit tests for core functionality
- Integration tests for end-to-end workflows
- GUI tests for interface validation
- Browser automation testing
- Error handling verification

### Running Tests

#### 1. Run All Tests

```bash
python -m pytest tests/ -v
```

#### 2. Run Specific Test Categories

```bash
# Core functionality tests
python -m pytest tests/test_data_handler.py -v

# Browser automation tests
python -m pytest tests/test_browser_automation.py -v

# GUI tests
python -m pytest tests/test_gui_functions.py -v

# Integration tests
python -m pytest tests/test_main_integration.py -v
```

#### 3. Run Tests with Coverage

```bash
python -m pytest tests/ --cov=src --cov-report=html
```

#### 4. Quick Feature Tests

```bash
# Test incremental save functionality
python tests/test_incremental_save.py

# Test request counter
python tests/test_request_counter.py

# Test metrics recovery
python tests/test_metrics_recovery.py
```

### Test Configuration

#### pytest.ini Configuration

The project includes optimized pytest settings:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --disable-warnings
```

#### Test Requirements

Install testing dependencies:

```bash
pip install -r test-requirements.txt
```

### Test Reports

#### 1. HTML Reports

Generate comprehensive HTML test reports:

```bash
python -m pytest tests/ --html=test_reports/report.html --self-contained-html
```

#### 2. XML Reports

For CI/CD integration:

```bash
python -m pytest tests/ --junit-xml=test_reports/junit.xml
```

#### 3. JSON Reports

For programmatic analysis:

```bash
python -m pytest tests/ --json-report --json-report-file=test_reports/report.json
```

### Test Utilities

#### 1. Test Logging Configuration

Advanced logging for test analysis:

```python
from tests.test_logging_config import setup_test_logging
setup_test_logging(log_level="DEBUG")
```

#### 2. Fixtures and Mock Data

Reusable test fixtures in `tests/fixtures.py`:

- Sample datasets
- Mock AI responses
- Browser automation mocks
- Temporary directory management

---

## 📊 Monitoring & Analytics

### Real-time Monitoring

#### 1. Request Tracking

Monitor API usage during processing:

- Request count per session
- Request rate (requests/minute)
- Estimated hourly consumption
- Quota usage warnings

#### 2. Progress Tracking

View processing progress:

- Completed batches
- Success/failure rates
- Remaining work estimates
- Session duration

### Metrics Analysis

#### 1. Execution Metrics

Analyze performance data:

```bash
python analyze_metrics.py --days 30 --detailed
```

#### 2. Metrics Visualization

Generate performance charts and trends:

```bash
python analyze_metrics.py --visualize --export-charts
```

#### 3. Historical Analysis

Compare session performance:

```bash
python analyze_metrics.py --compare-sessions --session-ids "20250901_120000,20250902_130000"
```

---

## 🆘 Support & Troubleshooting

### Log Analysis

1. Check `logs/YYYYMMDD_HHMMSS/` for session details
2. Review error screenshots in session folders
3. Examine `execution_metrics/` for performance data
4. Check `test_logs/` for test execution history

### Recovery Operations

1. **Corrupted metrics**: Run `python recover_metrics.py`
2. **Interrupted processing**: System auto-resumes from last save
3. **File structure issues**: Use tools in `tools/` directory
4. **Browser issues**: Clear `browser_data/` folder

### Best Practices

1. **Regular testing**: Run `python -m pytest tests/` before major processing
2. **Data validation**: Always validate input files before processing
3. **Backup strategy**: Keep copies of original datasets
4. **Resource monitoring**: Watch system resources during large jobs
5. **Incremental processing**: Use smaller batch sizes for better control

---

## 🎯 Tips for Success

### Performance Optimization

- Start with smaller batch sizes and increase gradually
- Monitor request rates to stay within quota limits
- Use debug mode to test configurations before full runs
- Regular cleanup of logs and temporary files

### Error Prevention

- Validate input data structure before processing
- Test with small datasets first
- Keep original files as backups
- Monitor system resources during processing

### Troubleshooting Workflow

1. Check logs for specific error messages
2. Validate input data and file structure
3. Test with debug mode using small dataset
4. Use recovery tools if corruption detected
5. Contact support with session logs if needed
