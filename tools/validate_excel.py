import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any

def validate_excel_columns(file_path: str) -> Dict[str, Any]:
    """
    Validates Excel file's column structure for automation compatibility
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        Dict with validation results containing:
        - valid (bool): True if file is valid for automation
        - issues (List[str]): List of issues found
        - column_status (Dict): Status for each required column
        - unprocessed_count (int): Number of unprocessed rows
    """
    results = {
        "valid": False,
        "issues": [],
        "column_status": {},
        "unprocessed_count": 0
    }
    
    # First check if file exists
    if not os.path.exists(file_path):
        results["issues"].append(f"File not found: {file_path}")
        return results
        
    # Try to load the file
    try:
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            results["issues"].append("Unsupported file format. Please use .xlsx or .csv")
            return results
    except Exception as e:
        results["issues"].append(f"Error opening file: {str(e)}")
        return results
        
    # Check file is not empty
    if len(df) == 0:
        results["issues"].append("File is empty (contains no data rows)")
        return results
    
    # Required columns for automation
    required_columns = {
        "full_text": {"alias": ["prompt", "question", "text"], "required": True},
        "label": {"alias": ["classification", "category"], "required": True}, 
        "justification": {"alias": ["explanation", "reason"], "required": True}
    }
    
    # Check for missing required columns
    available_columns = set(df.columns)
    
    # Initialize column status
    for col, info in required_columns.items():
        found = False
        used_name = None
        
        # Check for column or any of its aliases
        if col in available_columns:
            found = True
            used_name = col
        else:
            # Check aliases
            for alias in info["alias"]:
                if alias in available_columns:
                    found = True
                    used_name = alias
                    results["issues"].append(f"Using '{alias}' column as '{col}'")
                    break
                    
        # Record column status
        results["column_status"][col] = {
            "found": found,
            "used_name": used_name,
            "required": info["required"]
        }
        
        # Report missing required columns
        if not found and info["required"]:
            results["issues"].append(f"Missing required column: '{col}' or alternatives {info['alias']}")
    
    # If any required column is missing, return early
    if any(not status["found"] and status["required"] 
           for status in results["column_status"].values()):
        return results
    
    # Check for unprocessed rows
    if results["column_status"]["label"]["found"] and results["column_status"]["justification"]["found"]:
        label_col = results["column_status"]["label"]["used_name"]
        just_col = results["column_status"]["justification"]["used_name"]
        
        # Count rows with empty label or justification
        def is_empty(val):
            if pd.isna(val):  # Checks for NaN and None
                return True
            if isinstance(val, str) and val.strip() == '':  # Checks for empty strings and whitespace
                return True
            return False
            
        label_empty = df[label_col].apply(is_empty)
        just_empty = df[just_col].apply(is_empty)
        unprocessed_count = (label_empty | just_empty).sum()
        
        results["unprocessed_count"] = unprocessed_count
    
    # File is valid if we've reached this point
    results["valid"] = True
    
    # Add warning for potentially unnecessary columns
    unnecessary_cols = [col for col in df.columns 
                      if col not in [results["column_status"][rc]["used_name"] 
                                   for rc in required_columns
                                   if results["column_status"][rc]["found"]]]
    if unnecessary_cols:
        results["issues"].append(f"Found {len(unnecessary_cols)} potentially unnecessary columns: {', '.join(unnecessary_cols)}")
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python validate_excel.py <excel_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    results = validate_excel_columns(file_path)
    
    print(f"\n===== VALIDATION RESULTS FOR {file_path} =====")
    print(f"Valid for automation: {results['valid']}")
    
    if results["issues"]:
        print("\nIssues found:")
        for i, issue in enumerate(results["issues"], 1):
            print(f"{i}. {issue}")
    
    print("\nColumn status:")
    for col, status in results["column_status"].items():
        if status["found"]:
            print(f"✓ {col}: Found (as '{status['used_name']}')")
        else:
            print(f"✗ {col}: {'Missing (Required)' if status['required'] else 'Missing (Optional)'}")
    
    if "unprocessed_count" in results:
        print(f"\nUnprocessed rows: {results['unprocessed_count']}")
        
    print("\n===== END OF VALIDATION =====")
