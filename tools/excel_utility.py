#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel Utility Tool - Diagnoses and fixes Excel file issues

This utility helps diagnose and fix common issues with Excel files used in the automation system.
It provides commands for:
1. Diagnosing Excel files
2. Attempting to repair corrupted files
3. Checking for file locking issues
4. Validating data structure
"""

import os
import sys
import time
import pandas as pd
import argparse
from pathlib import Path

# Add the parent directory to sys.path to import our modules
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from src.data_handler import DataHandler

def is_file_locked(filepath):
    """
    Check if a file is locked by trying to open it in write mode
    
    Args:
        filepath (str): Path to the file to check
        
    Returns:
        bool: True if file is locked, False otherwise
    """
    locked = False
    if not os.path.exists(filepath):
        return False
        
    try:
        with open(filepath, 'a+b') as f:
            # If we can open it in write mode, it's not locked
            pass
    except (IOError, PermissionError):
        locked = True
    
    return locked

def diagnose_excel_file(filepath):
    """
    Run diagnostics on an Excel file
    
    Args:
        filepath (str): Path to the Excel file
    """
    print(f"Running diagnostics on {filepath}...")
    
    # Basic file checks
    print("\n=== Basic File Checks ===")
    print(f"File exists: {os.path.exists(filepath)}")
    if not os.path.exists(filepath):
        print("File doesn't exist. Aborting diagnostics.")
        return
        
    print(f"File size: {os.path.getsize(filepath)} bytes")
    print(f"Last modified: {time.ctime(os.path.getmtime(filepath))}")
    print(f"File is locked: {is_file_locked(filepath)}")
    
    # Try to open with DataHandler
    try:
        print("\n=== Using DataHandler to diagnose ===")
        handler = DataHandler(filepath)
        handler.diagnose_file(output_to_file=True)
        handler.close()
    except Exception as e:
        print(f"Error using DataHandler: {str(e)}")
        
    # Try to open with pandas directly
    try:
        print("\n=== Using pandas to diagnose ===")
        df = pd.read_excel(filepath)
        print(f"Successfully loaded with pandas. Shape: {df.shape}")
        print(f"Columns: {', '.join(df.columns.tolist())}")
        print(f"Data types:\n{df.dtypes}")
    except Exception as e:
        print(f"Error using pandas directly: {str(e)}")

def repair_excel_file(filepath):
    """
    Attempt to repair an Excel file
    
    Args:
        filepath (str): Path to the Excel file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(filepath):
        print(f"File doesn't exist: {filepath}")
        return False
    
    print(f"Attempting to repair {filepath}...")
    
    # Create a backup first
    backup_path = f"{filepath}.backup-{int(time.time())}"
    try:
        import shutil
        shutil.copy2(filepath, backup_path)
        print(f"Backup created at: {backup_path}")
    except Exception as e:
        print(f"Warning: Failed to create backup: {str(e)}")
        return False
    
    # Try to unlock file if it's locked
    if is_file_locked(filepath):
        print("File is locked. Attempting to unlock...")
        try:
            # On Windows, check for processes locking the file
            if sys.platform == 'win32':
                import psutil
                for proc in psutil.process_iter():
                    try:
                        for item in proc.open_files():
                            if filepath in item.path:
                                print(f"File is locked by process: {proc.name()} (PID: {proc.pid})")
                                break
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
        except ImportError:
            print("psutil not installed. Cannot check which process is locking the file.")
    
    # Try to repair using DataHandler
    try:
        handler = DataHandler(filepath)
        result = handler.repair_excel_file(backup=False)  # We already made a backup
        handler.close()
        if result:
            print("Repair successful!")
            return True
        else:
            print("Repair failed using DataHandler.")
    except Exception as e:
        print(f"Error during repair with DataHandler: {str(e)}")
    
    # Try manual repair as a fallback
    try:
        print("Attempting manual repair...")
        df = pd.read_excel(filepath)
        
        # Fix common issues:
        # 1. Remove duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]
        
        # 2. Convert problematic data types
        for col in df.columns:
            # Try to convert object columns with numbers to numeric
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
        
        # 3. Save back to Excel
        df.to_excel(filepath, index=False, engine='openpyxl')
        print("Manual repair completed successfully.")
        return True
    except Exception as e:
        print(f"Error during manual repair: {str(e)}")
        print(f"Original backup available at: {backup_path}")
        return False

def validate_data_structure(filepath):
    """
    Validate the data structure against expected schema
    
    Args:
        filepath (str): Path to the Excel file
    """
    required_columns = ['prompt', 'label', 'justification']
    
    try:
        df = pd.read_excel(filepath)
        print(f"Loaded file with {len(df)} rows")
        
        # Check for required columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            print(f"ERROR: Missing required columns: {', '.join(missing_cols)}")
        else:
            print("✓ All required columns present")
            
        # Check for empty cells in required columns
        for col in required_columns:
            if col in df.columns:
                empty_count = df[col].isna().sum()
                if empty_count > 0:
                    print(f"WARNING: Column '{col}' has {empty_count} empty values")
                else:
                    print(f"✓ Column '{col}' has no empty values")
        
        # Check for valid unprocessed data
        unprocessed_count = 0
        if 'label' in df.columns and 'justification' in df.columns:
            # Count rows where label is empty and justification is empty
            mask = (df['label'].isna() | (df['label'] == '')) & (df['justification'].isna() | (df['justification'] == ''))
            unprocessed_count = mask.sum()
            print(f"Found {unprocessed_count} unprocessed rows (empty label and justification)")
            
            # Show sample of first 5 unprocessed rows
            if unprocessed_count > 0:
                sample_unprocessed = df[mask].head(5)
                print("\nSample unprocessed rows (first 5):")
                for idx, row in sample_unprocessed.iterrows():
                    print(f"Row {idx}: prompt = \"{row['prompt'][:50]}...\"")
        
        return True
    except Exception as e:
        print(f"Error validating data structure: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Excel Utility Tool for automation system')
    parser.add_argument('command', choices=['diagnose', 'repair', 'check-lock', 'validate'],
                        help='Command to execute')
    parser.add_argument('filepath', help='Path to the Excel file')
    
    args = parser.parse_args()
    
    if args.command == 'diagnose':
        diagnose_excel_file(args.filepath)
    elif args.command == 'repair':
        repair_excel_file(args.filepath)
    elif args.command == 'check-lock':
        if is_file_locked(args.filepath):
            print(f"File is LOCKED: {args.filepath}")
            sys.exit(1)
        else:
            print(f"File is NOT locked: {args.filepath}")
            sys.exit(0)
    elif args.command == 'validate':
        validate_data_structure(args.filepath)

if __name__ == '__main__':
    main()
