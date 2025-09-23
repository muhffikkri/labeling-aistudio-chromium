# 🤖 AI Studio Auto-Labeling System

A production-ready automated text classification system that leverages Google's AI Studio platform through intelligent browser automation. Features robust error handling, comprehensive testing, and advanced monitoring capabilities.

## ✨ Key Features

- **🎯 Intelligent Browser Automation**: Playwright-based automation with multi-tier fallback strategies
- **📊 Batch Processing**: Configurable batch sizes with smart retry mechanisms and error recovery
- **🔄 Resume Capability**: Incremental progress saving with automatic resume from interruptions
- **📈 Real-time Monitoring**: API quota tracking, request rate monitoring, and performance metrics
- **🛡️ Self-healing System**: Automatic recovery from corrupted data and error conditions
- **🧪 Comprehensive Testing**: 90+ test cases with advanced reporting and coverage analysis
- **🔧 CLI Utilities**: Production tools for data validation, repair, and structure fixing
- **🎛️ GUI Interface**: User-friendly desktop interface for easy operation

## 🚀 Quick Start

### Automated Setup (Recommended)

**Windows:**

```batch
setup.bat
```

**macOS/Linux:**

```bash
chmod +x setup.sh && ./setup.sh
```

### Manual Installation

```bash
# 1. Clone and navigate
git clone <repository-url>
cd labeling-aistudio-chromium

# 2. Setup environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### What the Setup Scripts Do

**Automated Installation Process:**

1. **Python Detection**: Validates Python 3.8+ installation
2. **Environment Setup**: Creates isolated virtual environment
3. **Dependencies**: Installs all required packages from requirements.txt
4. **Validation**: Verifies installation success
5. **Launch**: Automatically starts the GUI application

**Error Handling:**

- Informative error messages for common issues
- Automatic fallback path detection
- Validation of each setup step
- Clear instructions for manual resolution

## 📖 Usage

### Command Line Interface

```bash
# Basic usage
python src/main.py --input-file "datasets/your_data.xlsx"

# Custom configuration
python src/main.py --input-file "datasets/data.xlsx" --batch-size 25 --debug
```

### GUI Interface

```bash
python src/gui.py
```

## 📁 Project Structure

```
├── src/                    # Main application code
│   ├── main.py            # CLI entry point
│   ├── gui.py             # GUI interface
│   └── core_logic/        # Core business logic
├── tests/                  # Comprehensive test suite (90+ tests)
├── tools/                  # CLI utilities for data management
├── datasets/              # Input data files
├── results/               # Processing outputs
├── logs/                  # Execution logs with session tracking
├── execution_metrics/     # Performance metrics and analytics
└── prompts/               # AI prompt templates
```

## � System Capabilities

### Processing Features

- ✅ Excel/CSV file support with auto-detection and repair
- ✅ Dynamic batch validation for partial batches
- ✅ Incremental progress saving to prevent data loss
- ✅ Smart retry logic with exponential backoff
- ✅ Failed row tracking and recovery mechanisms
- ✅ Automatic backup creation before processing

### Monitoring & Analytics

- ✅ Real-time API quota monitoring and rate limiting
- ✅ Request statistics tracking (count, rate, estimated usage)
- ✅ Performance metrics with historical analysis
- ✅ Session-based logging with debug artifacts
- ✅ Comprehensive error reporting and recovery tools

### Quality Assurance

- ✅ 90+ automated test cases covering all functionality
- ✅ Advanced test reporting (HTML, XML, JSON formats)
- ✅ Continuous integration ready with pytest configuration
- ✅ Code coverage analysis and reporting
- ✅ Mock data and fixture management for reliable testing

## 🔧 Advanced Features

### Error Recovery

- **JSON Metrics Recovery**: Automatic detection and repair of corrupted metrics files
- **Browser Crash Recovery**: Safe screenshot handling with fallback mechanisms
- **Process Interruption**: Resume from exact point of interruption with data integrity
- **File Corruption**: Atomic write operations prevent data corruption

### Performance Optimization

- **Request Rate Management**: Real-time monitoring prevents quota exhaustion
- **Memory Efficiency**: Optimized batch processing for large datasets
- **Resource Cleanup**: Automatic cleanup of temporary files and browser sessions
- **Concurrent Processing**: Safe parallel operations where applicable

## 📊 Monitoring Dashboard

Track processing progress and system health:

- Request rate and quota usage
- Processing success/failure rates
- Session duration and performance metrics
- Error tracking and resolution status
- Historical trends and regression analysis

## 🧪 Testing & Validation

```bash
# Run full test suite
python -m pytest tests/ -v --html=reports/test_report.html

# Run specific test categories
python -m pytest tests/test_core_logic.py -v
python -m pytest tests/test_browser_automation.py -v

# Run with coverage analysis
python -m pytest tests/ --cov=src --cov-report=html
```

## 🛠️ CLI Utilities

Validate and repair data files:

```bash
# Validate Excel/CSV structure
python tools/validate_excel.py datasets/your_file.xlsx

# Fix structural issues
python tools/fix_excel_structure.py datasets/your_file.xlsx

# Recover corrupted metrics
python recover_metrics.py
```

## 📈 Recent Improvements

### System Reliability

- **Self-healing JSON metrics** with automatic corruption recovery
- **Incremental save system** prevents data loss on interruption
- **Enhanced error handling** with comprehensive recovery mechanisms
- **Test organization** following Python best practices

### Monitoring Enhancements

- **Request counter system** for API quota management
- **Real-time rate monitoring** with usage predictions
- **Performance metrics tracking** with historical analysis
- **Comprehensive logging** with session-based organization

## 📚 Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)**: Complete usage, debugging, and testing guide
- **[CHANGELOG.md](CHANGELOG.md)**: Detailed history of improvements and fixes
- **[tools/README.md](tools/README.md)**: CLI utilities documentation

## 🆘 Troubleshooting

### Common Issues

1. **Browser automation**: Check Chrome installation and clear browser data
2. **File processing**: Use validation tools to check data structure
3. **API connection**: Verify Google AI Studio access and quota
4. **Memory issues**: Reduce batch size for large datasets

### Recovery Tools

- `python recover_metrics.py` - Fix corrupted metrics data
- `python tools/validate_excel.py` - Validate input file structure
- `python -m pytest tests/` - Verify system integrity
- Check `logs/` folder for detailed error information

## 🎯 Production Ready

This system is designed for production use with:

- **Robust error handling** and automatic recovery
- **Comprehensive testing** with 90+ automated test cases
- **Performance monitoring** and quota management
- **Data integrity protection** with incremental saves
- **Professional logging** and debugging capabilities

---

**🚀 Ready to automate your text classification workflow? Get started with the setup guide above!**

For detailed usage instructions, see **[USER_GUIDE.md](USER_GUIDE.md)**

### Basic Usage

#### 1. Prepare Your Data

```bash
# Place your Excel/CSV file in datasets folder
# Required columns: full_text, label (optional), justification (optional)

# Validate file structure
python -m tools.validate_excel "datasets/your_file.xlsx"

# Auto-fix structure if needed
python -m tools.fix_excel_structure "datasets/your_file.xlsx"
```

#### 2. Configure Prompts

```bash
# Edit prompt file (default: prompts/prompt.txt)
# Customize AI instructions for your classification task
```

#### 3. Run Processing

```bash
# Full processing
python src/main.py --input-file "datasets/your_file.xlsx"

# Debug mode (single batch)
python src/main.py --input-file "datasets/your_file.xlsx" --debug

# Custom batch size
python src/main.py --input-file "datasets/your_file.xlsx" --batch-size 25

# Custom prompt file
python src/main.py --input-file "datasets/your_file.xlsx" --prompt-file "prompts/custom_prompt.txt"
```

#### 4. Launch GUI Interface

```bash
# User-friendly desktop interface
python src/gui.py
```

### Advanced Usage

#### Data Management Tools

```bash
# Diagnose file issues
python -m tools.excel_utility diagnose "datasets/file.xlsx"

# Repair corrupted files
python -m tools.excel_utility repair "datasets/file.xlsx"

# Check file lock status
python -m tools.excel_utility check-lock "datasets/file.xlsx"

# Validate file structure
python -m tools.validate_excel "datasets/file.xlsx"

# Auto-fix structure with extra column removal
python -m tools.fix_excel_structure "datasets/file.xlsx" --remove-extra
```

#### Performance Metrics Analysis

```bash
# Show recent execution summary
python analyze_metrics.py summary

# Generate scatter plot of duration vs rows processed
python analyze_metrics.py scatter

# Show performance trends over time
python analyze_metrics.py trends

# Generate comprehensive analysis dashboard
python analyze_metrics.py analysis

# Show detailed regression analysis
python analyze_metrics.py regression

# Generate comprehensive report
python analyze_metrics.py report --output performance_report.txt

# Export data for external analysis
python analyze_metrics.py export --output metrics_data.csv
```

## 📊 Performance Metrics & Analysis

### Execution Tracking

The system automatically tracks comprehensive execution metrics for performance analysis and optimization:

- **⏱️ Duration Tracking**: Processing time for each session and batch
- **📊 Row Count Analysis**: Number of rows processed and success rates
- **🔍 Regression Analysis**: Statistical modeling of performance patterns
- **📈 Trend Analysis**: Performance trends over time with visualization

### Metrics Analysis Tools

```bash
# Quick performance summary
python analyze_metrics.py summary --days 7

# Generate performance visualizations
python analyze_metrics.py scatter       # Duration vs rows scatter plot
python analyze_metrics.py trends        # Performance trends over time
python analyze_metrics.py analysis      # Comprehensive dashboard

# Statistical analysis
python analyze_metrics.py regression    # Detailed regression analysis

# Export and reporting
python analyze_metrics.py report -o performance_report.txt
python analyze_metrics.py export -o data_for_analysis.csv
```

### Performance Insights

The metrics system provides valuable insights including:

- **📐 Linear Regression Models**: Predictive models for processing time based on data size
- **📊 R² Statistics**: Correlation strength between row count and processing duration
- **🔮 Performance Predictions**: Estimated processing times for different data sizes
- **📈 Trend Analysis**: Performance improvements or degradations over time

## 🧪 Testing & Quality Assurance

### Comprehensive Test Suite

Our application includes **90+ comprehensive tests** covering all components:

```bash
# Install test dependencies
pip install -r test-requirements.txt

# Run all tests with logging
python run_tests_with_logging.py --all

# Run specific test categories
python run_tests_with_logging.py --unit        # Unit tests only
python run_tests_with_logging.py --integration # Integration tests only
python run_tests_with_logging.py --gui         # GUI tests only
python run_tests_with_logging.py --browser     # Browser automation tests

# Generate coverage reports
python run_tests_with_logging.py --coverage

# Fast tests (exclude slow tests)
python run_tests_with_logging.py --fast
```

### Test Categories

| Test Type             | Count | Coverage                              |
| --------------------- | ----- | ------------------------------------- |
| **Unit Tests**        | 66    | Core logic, validation, data handling |
| **Integration Tests** | 13    | End-to-end workflows                  |
| **GUI Tests**         | 18    | Desktop interface components          |
| **Browser Tests**     | 19    | Automation and web interactions       |

### Test Analysis Tools

```bash
# Analyze test results and trends
python analyze_test_logs.py --recent 10     # Recent results
python analyze_test_logs.py --stats         # Comprehensive statistics
python analyze_test_logs.py --failures      # Failure analysis
python analyze_test_logs.py --trends 7      # Weekly trends
python analyze_test_logs.py --export data.csv # Export to CSV
```

## 🔍 Debugging & Troubleshooting

### Debug Mode

When encountering issues, always start with debug mode:

```bash
python src/main.py --input-file "datasets/your_file.xlsx" --debug
```

### Log Analysis

Each session generates a timestamped log folder in `logs/`:

- **run.log**: Main execution log with errors and warnings
- **Screenshots**: Visual debugging for browser automation issues
- **check*data_batch*\*.txt**: Validation details for failed batches
- **failed*rows*\*.xlsx**: Rows that failed processing

### Common Issues & Solutions

#### Browser Automation Issues

```bash
# Check screenshots in logs folder for visual debugging
# Clear browser data for fresh session
rm -rf browser_data/

# Test with reduced batch size
python src/main.py --input-file "datasets/file.xlsx" --batch-size 10
```

#### File Structure Issues

```bash
# Diagnose file problems
python -m tools.excel_utility diagnose "datasets/file.xlsx"

# Auto-fix common structure issues
python -m tools.fix_excel_structure "datasets/file.xlsx"
```

#### Validation Failures

Check `check_data_batch_*.txt` in log folders for:

- **Raw Response**: What AI returned
- **Full Prompt**: What was sent to AI
- **Validation Errors**: Specific validation failures

## 📁 File Structure Requirements

### Input Files

Your dataset files should contain:

- **full_text** (required): Text content to classify
- **label** (optional): Existing labels for validation
- **justification** (optional): Explanations for labels

### Supported Formats

- Excel files (.xlsx)
- CSV files (.csv)
- Automatic column detection and mapping

### Schema Flexibility

The system supports various column names through intelligent mapping:

- `full_text` ← prompt, question, text, content
- `label` ← classification, category, sentiment
- `justification` ← explanation, reason, rationale

## 🛠️ Development & Contribution

### Code Quality

- **Type Hints**: Comprehensive type annotations
- **Documentation**: Detailed docstrings and comments
- **Error Handling**: Robust exception handling with logging
- **Testing**: 90+ test cases with high coverage

### Contributing Guidelines

1. **Fork & Clone**: Create your own fork
2. **Environment**: Set up virtual environment
3. **Tests**: Ensure all tests pass (`python run_tests_with_logging.py --all`)
4. **Documentation**: Update relevant documentation
5. **Pull Request**: Submit with clear description

### Development Tools

```bash
# Run tests during development
python run_tests_with_logging.py --unit --fast

# Check code coverage
python run_tests_with_logging.py --coverage

# Validate tools functionality
python -m tools.validate_excel --help
```

## 📊 Performance & Scalability

### Batch Processing

- **Configurable batch sizes**: 10-100 rows per batch
- **Smart retry logic**: 3-tier retry with exponential backoff
- **Memory efficient**: Processes data in chunks
- **Resume capability**: Continue from interruption points

### Error Handling

- **Graceful degradation**: Multiple fallback strategies
- **Comprehensive logging**: Detailed error tracking
- **Failed row recovery**: Save and retry failed classifications
- **Session recovery**: Resume interrupted sessions

## 🔐 Security & Privacy

### Data Handling

- **Local processing**: No data sent to external services except AI Studio
- **Temporary files**: Automatic cleanup of temporary data
- **Backup safety**: Original files preserved during processing
- **Session isolation**: Each session uses isolated browser contexts

### Browser Automation

- **Stealth techniques**: Anti-detection measures
- **Session management**: Proper cookie and session handling
- **Resource cleanup**: Automatic browser resource cleanup

## 🎯 Supported Classification Tasks

### Text Classification

- **Sentiment Analysis**: Positive/Negative/Neutral classification
- **Topic Classification**: Multi-class topic categorization
- **Intent Detection**: User intent classification
- **Custom Categories**: Flexible label configuration

### Output Formats

- **Labeled Dataset**: Original data with added classifications
- **Justifications**: AI-generated explanations for decisions
- **Confidence Scores**: Classification confidence levels
- **Validation Reports**: Data quality and processing statistics

## 📈 Version History & Roadmap

### Current Features ✅

- ✅ Browser automation with Playwright
- ✅ Comprehensive testing infrastructure (90+ tests)
- ✅ Advanced logging and debugging tools
- ✅ CLI utilities for data management
- ✅ GUI interface for easy operation
- ✅ Robust error handling and recovery
- ✅ Session-based processing with resume capability
- ✅ Performance metrics tracking with regression analysis
- ✅ CLI tools for metrics visualization and reporting

### Upcoming Features 🚀

- 🔄 API integration alternatives
- 📊 Advanced analytics and reporting
- 🔌 Plugin system for custom processors
- 🌐 Multi-language support
- ☁️ Cloud deployment options

## 🆘 Support & Resources

### Documentation

- **README.md**: This comprehensive guide
- **GUIDE_COMPREHENSIVE_TESTING.md**: Detailed testing documentation
- **TEST_LOGGING_IMPLEMENTATION.md**: Test logging system details
- **TOOLS_ANALYSIS.md**: Utility tools analysis and usage

### Getting Help

1. **Check logs**: Review session logs in `logs/` folder
2. **Run diagnostics**: Use tools utilities for file validation
3. **Debug mode**: Run with `--debug` flag for detailed output
4. **Test validation**: Run test suite to verify installation

### Community & Contribution

- **Issues**: Report bugs and feature requests
- **Pull Requests**: Contribute code improvements
- **Documentation**: Help improve guides and examples

---

## � License

This project is licensed under the **MIT License** - see the LICENSE file for details.

---

**🎉 Ready to automate your text classification workflow? Get started with the installation guide above!**
