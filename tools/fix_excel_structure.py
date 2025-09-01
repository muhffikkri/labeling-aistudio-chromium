#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel Structure Fixer

This tool fixes common structural problems in Excel files for the automation system.
It can:
1. Add missing required columns
2. Rename columns to expected names
3. Fix data types
4. Remove unnecessary columns if requested
"""

import os
import sys
import pandas as pd
import numpy as np
import argparse
from pathlib import Path
import shutil

# Add the parent directory to sys.path to import our modules
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from tools.validate_excel import validate_excel_columns

def fix_excel_structure(file_path, make_backup=True, remove_extra=False, verbose=True):
    """
    Fix common structural issues in Excel files for automation
    
    Args:
        file_path (str): Path to the Excel file
        make_backup (bool): Whether to create a backup before modifying
        remove_extra (bool): Whether to remove unnecessary columns
        verbose (bool): Whether to print detailed information
        
    Returns:
        bool: True if successful, False otherwise
    """
    def log(msg):
        if verbose:
            print(msg)
    
    # Validate first
    log(f"Validating {file_path}...")
    validation = validate_excel_columns(file_path)
    
    if not os.path.exists(file_path):
        log(f"Error: File not found: {file_path}")
        return False
        
    # Make backup if requested
    if make_backup:
        backup_path = f"{file_path}.backup"
        try:
            shutil.copy2(file_path, backup_path)
            log(f"Created backup at {backup_path}")
        except Exception as e:
            log(f"Warning: Could not create backup: {str(e)}")
            return False
    
    # Try to load the file
    try:
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            log(f"Error: Unsupported file format: {file_path}")
            return False
    except Exception as e:
        log(f"Error opening file: {str(e)}")
        return False
    
    # Get required columns mapped to their found names or None if missing
    required_columns = {
        "full_text": ["prompt", "question", "text"],
        "label": ["classification", "category"],
        "justification": ["explanation", "reason"]
    }
    
    column_mapping = {}  # Original name -> target name
    columns_to_create = []
    
    # Check each required column
    for target_col, alternatives in required_columns.items():
        if target_col in df.columns:
            # Column already exists with correct name
            log(f"✓ Column '{target_col}' exists with correct name")
            continue
            
        # Look for alternative column names
        found = False
        for alt_col in alternatives:
            if alt_col in df.columns:
                column_mapping[alt_col] = target_col
                found = True
                log(f"Column '{alt_col}' will be renamed to '{target_col}'")
                break
                
        if not found:
            columns_to_create.append(target_col)
            log(f"Column '{target_col}' will be created")
    
    # Apply column mapping (rename columns)
    if column_mapping:
        df = df.rename(columns=column_mapping)
        log(f"Renamed {len(column_mapping)} columns")
    
    # Create missing columns
    for col in columns_to_create:
        df[col] = np.nan
        log(f"Created empty column: {col}")
        
        # If this is the text/prompt column, we need to alert the user
        if col == "full_text":
            log("WARNING: Created empty 'full_text' column. You must add content to this column!")
    
    # Remove extra columns if requested
    if remove_extra:
        required_cols = list(required_columns.keys())
        extra_columns = [col for col in df.columns if col not in required_cols]
        
        if extra_columns:
            log(f"Removing {len(extra_columns)} unnecessary columns: {', '.join(extra_columns)}")
            df = df[required_cols]
    
    # Fix data types - ensure all columns are string type
    for col in df.columns:
        if col in required_columns or col in ["full_text", "label", "justification"]:
            if df[col].dtype != 'object':
                log(f"Converting {col} from {df[col].dtype} to string type")
                df[col] = df[col].astype(str)
                # Replace 'nan' string with actual NaN
                df[col] = df[col].replace('nan', np.nan)
    
    # Save the changes
    try:
        if file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        elif file_path.endswith('.csv'):
            df.to_csv(file_path, index=False)
        log(f"Successfully saved changes to {file_path}")
        
        # Validate again to confirm fixes
        fixed_validation = validate_excel_columns(file_path)
        
        if fixed_validation["valid"]:
            log("\n✅ File structure has been fixed successfully!")
            log(f"Unprocessed rows: {fixed_validation['unprocessed_count']}")
            return True
        else:
            log("\n⚠️ Some issues remain after fixing:")
            for issue in fixed_validation["issues"]:
                log(f"- {issue}")
            return False
            
    except Exception as e:
        log(f"Error saving file: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Fix Excel file structure for automation compatibility'
    )
    parser.add_argument('file_path', help='Path to the Excel or CSV file')
    parser.add_argument('--no-backup', action='store_true', 
                        help='Do not create a backup file')
    parser.add_argument('--remove-extra', action='store_true',
                        help='Remove unnecessary columns')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress detailed output')
    
    args = parser.parse_args()
    
    fix_excel_structure(
        args.file_path,
        make_backup=not args.no_backup,
        remove_extra=args.remove_extra,
        verbose=not args.quiet
    )

if __name__ == "__main__":
    main()
