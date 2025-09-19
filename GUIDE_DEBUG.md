# 🔍 Debugging & Troubleshooting Guide

When issues occur, follow this systematic debugging approach. **Philosophy**: Everything you need for debugging is contained within the session log folder.

## 🚨 Quick Debug Workflow

### Step 1: Run in Debug Mode

Always start troubleshooting with debug mode - it processes only one batch and creates a clean log folder:

```bash
python src/main.py --input-file "datasets/your_file.xlsx" --debug
```

### Step 2: Locate Session Log Folder

Navigate to `logs/` directory and find the newest timestamped folder (e.g., `2025-09-19_14-30-45`).

### Step 3: Analyze Debug Artifacts (In This Order)

## 📋 Debug File Analysis

### 1. **run.log** - Start Here ⭐

- **Primary debug source** - check this file first
- Look for **ERROR** or **CRITICAL** messages near the bottom
- Read **WARNING** messages for non-fatal issues
- Contains full error tracebacks showing exactly what went wrong

### 2. **Screenshots (.png)** - Visual Debugging

When `run.log` shows browser-related errors:

- **FATAL_ERROR_timeout.png** - Browser timeout issues
- **ERROR_extraction_failed.png** - Page interaction failures
- Shows exactly what the browser saw during errors

### 3. **check*data_batch*\*.txt** - Validation Details

For validation failures, examine:

- **RAW RESPONSE** - What AI actually returned
- **FULL PROMPT** - What was sent to AI
- **Validation Issues** - Specific validation failures
- Compare format expectations vs actual output

### 4. **failed*rows*\*.xlsx** - Failed Data

- Contains original rows that failed after all retry attempts
- Check for unusual text content that might cause issues
- Use for data quality analysis

## 🔧 Common Issue Scenarios

### Browser Automation Problems

**Symptoms**: Timeouts, login failures, element not found

```bash
# Check visual evidence
# View: logs/TIMESTAMP/FATAL_ERROR_timeout.png

# Solutions:
# 1. Clear browser data for fresh session
rm -rf browser_data/

# 2. Test manual login first
# 3. Reduce batch size for stability
python src/main.py --input-file "datasets/file.xlsx" --batch-size 10
```

### Validation Failures

**Symptoms**: "Validation Failed: Row count mismatch" or "Invalid labels found"

**Analysis Process:**

1. Open `check_data_batch_*.txt`
2. Compare **RAW RESPONSE** with input data
3. Check if AI returned correct number of rows
4. Verify labels match allowed values

**Solutions:**

```bash
# Common fixes:
# 1. Adjust prompts/prompt.txt for clearer instructions
# 2. Check ALLOWED_LABELS in src/core_logic/validation.py
# 3. Reduce batch size to improve AI accuracy
```

### File Structure Issues

**Symptoms**: Column not found errors, data loading failures

```bash
# Diagnose file structure
python -m tools.validate_excel "datasets/your_file.xlsx"

# Auto-fix common issues
python -m tools.fix_excel_structure "datasets/your_file.xlsx"

# Check for file corruption
python -m tools.excel_utility diagnose "datasets/your_file.xlsx"
```

### Performance Issues

**Symptoms**: Slow processing, memory issues, frequent timeouts

```bash
# Solutions:
# 1. Reduce batch size
python src/main.py --input-file "datasets/file.xlsx" --batch-size 15

# 2. Check system resources
# 3. Close other applications
# 4. Use debug mode to test individual batches
```

## 📊 Log File Patterns

### Success Patterns in run.log

```
INFO - ✅ Batch 1 processed successfully
INFO - ✅ All validation checks passed
INFO - 📄 Results saved to: results/processed_data.xlsx
```

### Error Patterns to Look For

```
ERROR - ❌ Browser timeout after 30 seconds
ERROR - ❌ Validation failed: Row count mismatch
CRITICAL - ❌ Failed to extract AI response
WARNING - ⚠️ Retry attempt 2/3 for batch
```

## 🛠️ Advanced Debugging Techniques

### Browser Automation Debugging

```bash
# Enable verbose browser logs
PLAYWRIGHT_DEBUG=1 python src/main.py --debug --input-file "datasets/file.xlsx"

# Check browser console logs in screenshots
# Look for JavaScript errors or network issues
```

### Validation Debugging

```bash
# Test specific validation logic
python -c "
from src.core_logic.validation import ValidationLogic
validator = ValidationLogic()
# Test with sample data
"
```

### Data Handler Debugging

```bash
# Test file loading separately
python -c "
from src.core_logic.data_handler import DataHandler
handler = DataHandler('datasets/your_file.xlsx')
print(handler.get_unprocessed_count())
"
```

## 🎯 Prevention Best Practices

### Before Processing

```bash
# 1. Validate data structure
python -m tools.validate_excel "datasets/file.xlsx"

# 2. Test with debug mode
python src/main.py --input-file "datasets/file.xlsx" --debug

# 3. Check file for issues
python -m tools.excel_utility diagnose "datasets/file.xlsx"
```

### During Processing

- Monitor console output for warnings
- Check `logs/` folder for new session creation
- Watch for browser window behavior

### After Issues

- Always check newest session folder in `logs/`
- Review screenshots before attempting fixes
- Save debug artifacts for analysis

## 🚀 Recovery Procedures

### Session Recovery

```bash
# Application automatically resumes processing
# Just run the same command again
python src/main.py --input-file "datasets/file.xlsx"
```

### Data Recovery

```bash
# Check results folder for partial processing
ls results/

# Combine with failed_rows files if needed
# Manual review of failed_rows_*.xlsx files
```

### Clean Start

```bash
# If complete reset needed:
rm -rf browser_data/  # Clear browser session
rm -rf logs/latest_*  # Clear recent logs
# Then retry processing
```

---

## 📞 When to Seek Additional Help

Contact for support if:

- Debug artifacts don't show clear error cause
- Issues persist after following troubleshooting steps
- Browser automation completely fails
- File corruption or data loss occurs

**🎯 Remember: The session log folder contains everything needed for debugging - start there first!**
