# 🤖 AI Studio Auto-Labeling System

A comprehensive automated text dataset labeling application that leverages Google's AI Studio platform through intelligent browser automation. This system provides robust data processing, comprehensive testing infrastructure, and powerful utility tools for production-ready text classification workflows.

## ✨ Key Features

### Core Functionality

- **🎯 Intelligent Browser Automation**: Uses Playwright with multi-tier fallback strategies for reliable AI Studio interactions
- **📊 Batch Processing**: Configurable batch sizes with smart retry mechanisms and error handling
- **✅ Advanced Validation**: Comprehensive response validation with automatic retry logic for failed classifications
- **🔄 Resume Capability**: Intelligent resume functionality that continues from where it left off

### Development & Production Tools

- **🧪 Comprehensive Testing Suite**: 90+ test cases covering unit, integration, GUI, and browser automation testing
- **📈 Test Logging System**: Advanced logging with JSON, XML, and HTML reports for test analysis and trending
- **🛠️ CLI Utilities**: Production-ready tools for Excel file diagnostics, repair, and validation
- **🎛️ GUI Interface**: User-friendly desktop interface for easy operation
- **📝 Session-Based Logging**: Detailed execution logs with screenshots and debug artifacts for troubleshooting
- **📊 Performance Metrics**: Comprehensive execution tracking with duration analysis, regression modeling, and visualization tools

### Data Management

- **📋 Excel/CSV Support**: Robust handling of various file formats with automatic structure detection
- **🔧 Auto-Repair Tools**: Smart file structure fixing with column mapping and validation
- **📁 Failed Row Tracking**: Comprehensive error tracking and recovery mechanisms
- **💾 Backup Strategy**: Automatic backups before any file modifications

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.8+** (Recommended: Python 3.12)
- **Google Chrome** (for browser automation)
- **Windows/macOS/Linux** support

### Quick Installation

#### Option 1: Automated Setup (Recommended)

**For Windows:**

```batch
# Double-click setup.bat or run in Command Prompt:
setup.bat
```

**For macOS/Linux:**

```bash
# Make script executable and run:
chmod +x setup.sh
./setup.sh
```

#### Option 2: Manual Setup

```bash
# 1. Clone repository
git clone <REPOSITORY_URL>
cd labeling-aistudio-chromium

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install testing dependencies (optional)
pip install -r test-requirements.txt
```

### Project Structure

```
labeling-aistudio-chromium/
├── src/                    # Main application code
│   ├── main.py            # Entry point
│   ├── gui.py             # Desktop GUI interface
│   └── core_logic/        # Core business logic
├── tests/                  # Comprehensive test suite (90+ tests)
├── tools/                  # CLI utilities for data management
├── datasets/              # Input data files (.xlsx/.csv)
├── prompts/               # AI prompts and instructions
├── results/               # Processed output files
├── logs/                  # Session execution logs
├── execution_metrics/     # Performance metrics and analysis data
├── test_logs/             # Test execution logs and reports
└── analyze_metrics.py     # CLI tool for metrics analysis
```

## 🏃‍♂️ Usage Guide

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
