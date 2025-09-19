# 🚀 Application Usage Guide

This guide provides specific instructions for running the main application after installation.

## 🎯 Quick Start

### Basic Command Structure

All commands are run from the **project root directory**:

```bash
python src/main.py [ARGUMENTS]
```

### Required Setup

1. **Data file**: Place your Excel/CSV file in `datasets/` folder
2. **Prompt file**: Customize `prompts/prompt.txt` for your classification task
3. **Virtual environment**: Ensure your Python environment is activated

## 📋 Command-Line Arguments

| Argument        | Description                                | Required | Default              |
| --------------- | ------------------------------------------ | -------- | -------------------- |
| `--input-file`  | Path to dataset file in `datasets/` folder | ✅ Yes   | -                    |
| `--prompt-file` | Path to prompt file                        | ❌ No    | `prompts/prompt.txt` |
| `--batch-size`  | Rows processed per batch                   | ❌ No    | 50                   |
| `--debug`       | Debug mode (processes only one batch)      | ❌ No    | -                    |

## 💡 Usage Examples

### 1. Standard Processing

Process entire dataset with default settings:

```bash
python src/main.py --input-file "datasets/my_data.xlsx"
```

### 2. Custom Batch Size

Adjust batch size for performance or reliability:

```bash
python src/main.py --input-file "datasets/my_data.xlsx" --batch-size 25
```

### 3. Debug Mode

Test processing with single batch for debugging:

```bash
python src/main.py --input-file "datasets/my_data.xlsx" --debug
```

### 4. Custom Prompt

Use different prompt file:

```bash
python src/main.py --input-file "datasets/my_data.xlsx" --prompt-file "prompts/custom_prompt.txt"
```

### 5. Combined Options

```bash
python src/main.py --input-file "datasets/my_data.xlsx" --batch-size 30 --prompt-file "prompts/sentiment_analysis.txt"
```

## 📁 File Requirements

### Input Data Format

Your dataset file must contain:

- **full_text** column: Text content to classify
- **label** column (optional): Existing labels for validation
- **justification** column (optional): Explanations for labels

### Supported File Types

- Excel files (`.xlsx`)
- CSV files (`.csv`)

### File Validation

Before running the main application:

```bash
# Validate file structure
python -m tools.validate_excel "datasets/your_file.xlsx"

# Auto-fix structure if needed
python -m tools.fix_excel_structure "datasets/your_file.xlsx"
```

## 🔄 Processing Workflow

1. **File Loading**: Reads and validates input file
2. **Batch Creation**: Splits data into configurable batches
3. **Browser Launch**: Starts automated browser session
4. **AI Processing**: Sends batches to AI Studio for classification
5. **Validation**: Validates AI responses and retry failed batches
6. **Result Saving**: Saves processed data to results folder
7. **Session Logging**: Creates detailed logs for debugging

## 📊 Expected Output

### Result Files

- **Processed Dataset**: Original data with added labels and justifications
- **Session Logs**: Timestamped folder in `logs/` with execution details
- **Failed Rows**: Separate file for any rows that couldn't be processed

### Log Structure

```
logs/YYYY-MM-DD_HH-MM-SS/
├── run.log                    # Main execution log
├── screenshots/               # Browser automation screenshots
├── check_data_batch_*.txt     # Validation details
└── failed_rows_*.xlsx         # Failed processing data
```

## 🎮 GUI Alternative

For a user-friendly interface, launch the desktop GUI:

```bash
python src/gui.py
```

The GUI provides:

- File selection dialog
- Parameter configuration
- Real-time progress monitoring
- Log viewing

## ⚡ Performance Tips

### Batch Size Optimization

- **Small batches (10-25)**: Better for unstable connections
- **Medium batches (25-50)**: Good balance (default)
- **Large batches (50-100)**: Faster processing for stable setups

### Debug Mode Benefits

- Quick validation of setup
- Test prompt effectiveness
- Verify file structure
- Troubleshoot issues without full processing

### Resume Processing

The application automatically resumes from where it left off if interrupted. It skips already processed rows.

## 🔧 Troubleshooting

### Common Issues

**File not found error:**

```bash
# Ensure file is in datasets folder
ls datasets/
python src/main.py --input-file "datasets/existing_file.xlsx"
```

**Permission denied error:**

```bash
# Close Excel if file is open
# Use smaller batch size
python src/main.py --input-file "datasets/file.xlsx" --batch-size 10
```

**Browser automation issues:**

```bash
# Run in debug mode first
python src/main.py --input-file "datasets/file.xlsx" --debug
# Check screenshots in generated log folder
```

### Debug Information

When issues occur:

1. **Check logs**: Review `logs/latest_session/run.log`
2. **Screenshot review**: Examine browser screenshots for UI issues
3. **Validation files**: Check `check_data_batch_*.txt` for AI response issues
4. **Use debug mode**: Run single batch with `--debug` flag

---

**📚 For more detailed troubleshooting, see the comprehensive README.md debugging section.**
