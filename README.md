# Browser Automation App

This project automates the process of labeling datasets using the AI Studio platform at aistudio.google.com. The automation script interacts with a dataset in Excel format, sends data for labeling, and updates the dataset with the results.

## Browser Automation App

This is a Python application for automating browser interactions to interact with Google AI Studio.

### Features

- Automated browser interaction with Google AI Studio
- Excel data processing and management
- Error handling and recovery
- Dynamic waiting for response generation
- Excel file validation and repair tools

## Installation

1. Clone this repository
2. Install dependencies with `pip install -r requirements.txt`
3. Set up your data file (Excel or CSV)
4. Run the application with `python main.py`

## Excel Utility Tools

The application comes with several utility tools for working with Excel files:

### Excel Diagnostics

Check and diagnose issues with Excel files:

```powershell
python tools/excel_utility.py diagnose path/to/your/file.xlsx
```

### Excel File Repair

Attempt to repair corrupted Excel files:

```powershell
python tools/excel_utility.py repair path/to/your/file.xlsx
```

### Check File Lock Status

Check if an Excel file is currently locked by another process:

```powershell
python tools/excel_utility.py check-lock path/to/your/file.xlsx
```

### Validate Excel Structure

Validate that Excel file has the correct structure for automation:

```powershell
python tools/validate_excel.py path/to/your/file.xlsx
```

### Fix Excel Structure

Fix issues with Excel file structure for automation compatibility:

```powershell
python tools/fix_excel_structure.py path/to/your/file.xlsx
```

Options:
- `--no-backup` - Don't create a backup file
- `--remove-extra` - Remove unnecessary columns
- `--quiet` - Reduce output verbosity

2. **Process Overview:**
   - The script will read the dataset, extract the required text, and send it to AI Studio for labeling.
   - It will handle responses, update the dataset with labels and justifications, and verify the results.
   - If discrepancies are found, the script will retry sending the data.
   - After every five requests, the script will clear the chat history to optimize memory usage.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.