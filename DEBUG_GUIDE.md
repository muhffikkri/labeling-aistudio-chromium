# Browser Automation App - Debug Guide

This guide explains how to use the debugging tools added to diagnose response extraction issues from Gemini AI.

## The Problem

The application is experiencing issues extracting responses from Google's Gemini AI Studio. Specifically:

- The response is generated in the UI but cannot be properly extracted using the current selectors
- This results in empty results being returned even when the AI has generated a response

## Debugging Tools Added

I've enhanced the code with advanced debugging capabilities:

### 1. Enhanced Response Extraction

The `process_batch` method now includes multiple strategies to extract the response:

- **METHOD 1**: Direct DOM selectors targeting various response elements
- **METHOD 2**: JavaScript-based extraction looking for specific label keywords 
- **METHOD 3**: DOM structure exploration to find all potential response content
- **EMERGENCY METHOD**: HTML content analysis as a last resort

### 2. Detailed Diagnostics

- **Screenshots** taken at critical points in the process:
  - `before_response_gen_[timestamp].png`: UI state before sending prompt
  - `generation_started_[timestamp].png`: When generation starts
  - `after_response_gen_[timestamp].png`: After response is generated
  - `response_extraction_[timestamp].png`: During response extraction
  - Various error screenshots when issues are encountered

- **Debug Logging** with detailed information about:
  - DOM elements found
  - Response content previews 
  - Extraction method success/failure

### 3. Debug Mode Script

A new `main_debug.py` script that:
- Processes just a single batch and stops
- Uses a smaller batch size (10 items)
- Provides detailed feedback on results

## How to Use the Debug Tools

### Step 1: Run Debug Mode

```bash
python main_debug.py
```

This will:
1. Launch the browser
2. Wait for you to log in manually if needed
3. Process a single small batch
4. Create detailed screenshots and logs
5. Exit after completing the single batch

### Step 2: Analyze Debug Information

1. Review the **console output** which contains detailed step-by-step logging
2. Examine the **screenshot files** generated during the process
3. Look for specific errors or issues reported in the extraction phase

### Step 3: Identify the Issue

Based on the debug information, you can determine:
- If the UI structure has changed (requiring updated selectors)
- If there are permission issues preventing generation
- If responses are being generated but not captured correctly

## Key Files

- `main_debug.py` - Debug-focused version of the main application
- `src/automation.py` - Contains the enhanced extraction methods
- Screenshots - Various PNG files generated during debugging

## Common Issues & Solutions

1. **Permission Denied**: Shown in error screenshots - reduce batch size or wait longer between requests
2. **Changed UI Structure**: Look at DOM path information to update selectors
3. **Response Not Found**: Check if responses match expected format (POSITIF - justification, etc.)

## Next Steps

After identifying the issue:

1. Update selectors if the UI has changed
2. Adjust parsing logic if response format has changed
3. Update the main application with the corrected extraction logic
