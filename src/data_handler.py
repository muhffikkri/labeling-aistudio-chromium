import os
import time
import pandas as pd
import numpy as np
from typing import List, Tuple

class DataHandler:
    def __init__(self, file_path: str):
        """
        Initializes the DataHandler with the path to the dataset file.

        Args:
            file_path (str): The path to the .xlsx or .csv file.
        """
        self.file_path = file_path
        print(f"DataHandler: Initializing with file: {os.path.abspath(file_path)}")
        
        try:
            if file_path.endswith('.xlsx'):
                self.df = pd.read_excel(file_path)
                print(f"Successfully read Excel file with {len(self.df)} rows")
            elif file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
                print(f"Successfully read CSV file with {len(self.df)} rows")
            else:
                raise ValueError("Unsupported file format. Please use .xlsx or .csv")
                
            # Reset internal cache of pandas
            self.df = self.df.reset_index(drop=True)
            
        except FileNotFoundError:
            print(f"Error: The file at {file_path} was not found.")
            # Create an empty DataFrame with expected columns if file not found
            self.df = pd.DataFrame(columns=['full_text', 'label', 'justification'])

        # Pastikan kolom 'label' dan 'justification' ada. Jika tidak, buat kolom kosong.
        if 'label' not in self.df.columns:
            print("Column 'label' not found. Creating it.")
            # Use np.nan explicitly for better compatibility
            self.df['label'] = np.nan
            # Save immediately to ensure column is persistent
            self.save_data()
            print("Added 'label' column and saved the file")
            
        if 'justification' not in self.df.columns:
            print("Column 'justification' not found. Creating it.")
            # Use np.nan explicitly for better compatibility
            self.df['justification'] = np.nan
            # Save immediately to ensure column is persistent
            self.save_data()
            print("Added 'justification' column and saved the file")
            
        # Ensure all empty strings are converted to NaN for consistent processing
        if 'label' in self.df.columns:
            self.df['label'] = self.df['label'].replace('', np.nan)
        if 'justification' in self.df.columns:
            self.df['justification'] = self.df['justification'].replace('', np.nan)
            
        # Verify columns were added successfully
        print(f"Verification: DataFrame now has columns: {', '.join(self.df.columns)}")
        print(f"Total rows: {len(self.df)}")
        
        # Debug info about empty values
        if 'label' in self.df.columns:
            null_labels = self.df['label'].isnull().sum()
            print(f"Rows with NaN in 'label' column: {null_labels}")
        if 'justification' in self.df.columns:
            null_just = self.df['justification'].isnull().sum()
            print(f"Rows with NaN in 'justification' column: {null_just}")


    def get_data_batches(self, batch_size: int = 100) -> List[List[str]]:
        """
        Splits the 'full_text' column into batches of a specified size.

        Args:
            batch_size (int): The number of items per batch.

        Returns:
            List[List[str]]: A list of batches, where each batch is a list of strings.
        """
        if 'full_text' not in self.df.columns:
            print("Error: 'full_text' column not found in the dataset.")
            return []
        
        # Get unprocessed data
        unprocessed_df = self.df[self.df['label'].isnull() | self.df['justification'].isnull()]
        
        texts = unprocessed_df['full_text'].tolist()
        return [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]

    def update_and_save_data(self, results: List[Tuple[str, str]], start_index: int):
        """
        Updates the DataFrame with labels and justifications and saves it back to the file.

        Args:
            results (List[Tuple[str, str]]): A list of tuples, each containing (label, justification).
            start_index (int): The starting index in the original DataFrame to update from.
        """
        if 'label' not in self.df.columns:
            self.df['label'] = None
        if 'justification' not in self.df.columns:
            self.df['justification'] = None

        # Get the indices of unprocessed rows
        unprocessed_indices = self.df[self.df['label'].isnull() | self.df['justification'].isnull()].index
        
        # If there are no unprocessed rows, use a sequential update approach
        if len(unprocessed_indices) == 0:
            # Default to updating from the beginning of the DataFrame
            print("No unprocessed rows found. Using sequential update from the start.")
            start_row = 0
            indices_to_update = self.df.index[start_row : start_row + len(results)]
        else:
            # If start_index is too large, reset to 0 to avoid index error
            if start_index >= len(unprocessed_indices):
                print(f"Warning: Requested start_index {start_index} exceeds available unprocessed data count {len(unprocessed_indices)}.")
                print("Resetting to first unprocessed row.")
                start_index = 0
                
            # Determine the actual indices to update
            indices_to_update = unprocessed_indices[start_index : start_index + len(results)]

        for i, (label, justification) in enumerate(results):
            if i < len(indices_to_update):
                actual_index = indices_to_update[i]
                self.df.loc[actual_index, 'label'] = label
                self.df.loc[actual_index, 'justification'] = justification

        self.save_data()

    def save_data(self):
        """Saves the DataFrame back to the original file."""
        try:
            if self.file_path.endswith('.xlsx'):
                self.df.to_excel(self.file_path, index=False)
            elif self.file_path.endswith('.csv'):
                self.df.to_csv(self.file_path, index=False)
            print(f"Data successfully saved to {self.file_path}")
        except Exception as e:
            print(f"Error saving data: {e}")

    def get_unprocessed_data_count(self) -> int:
        """
        Counts the number of rows that have not been labeled or justified.
        Improved to detect empty strings as well as NaN values.
        """
        # Add debugging information to identify issues with data detection
        print(f"\nDEBUG: Checking for unprocessed data in {self.file_path}")
        print(f"DEBUG: Total rows in dataframe: {len(self.df)}")
        print(f"DEBUG: Columns in dataframe: {', '.join(self.df.columns)}")
        
        if 'label' not in self.df.columns:
            print("DEBUG: 'label' column is missing from dataframe")
            return 0
        
        if 'justification' not in self.df.columns:
            print("DEBUG: 'justification' column is missing from dataframe")
            return 0
            
        # More aggressive check - considers empty strings, whitespace, None, and NaN as empty
        def is_empty(val):
            if pd.isna(val):  # Checks for NaN and None
                return True
            if isinstance(val, str) and val.strip() == '':  # Checks for empty strings and whitespace
                return True
            return False
        
        # Apply more comprehensive emptiness check
        label_empty = self.df['label'].apply(is_empty)
        justification_empty = self.df['justification'].apply(is_empty)
        
        # Calculate unprocessed rows with detailed logging
        label_null_count = label_empty.sum()
        justification_null_count = justification_empty.sum()
        combined_empty_count = (label_empty | justification_empty).sum()
        
        print(f"DEBUG: Rows with empty 'label': {label_null_count}")
        print(f"DEBUG: Rows with empty 'justification': {justification_null_count}")
        print(f"DEBUG: Total unprocessed rows: {combined_empty_count}")
        
        # As a fallback, also show the traditional NaN counting
        traditional_null_count = self.df[self.df['label'].isnull() | self.df['justification'].isnull()].shape[0]
        print(f"DEBUG: (Using traditional NaN check): {traditional_null_count}")
        
        # Use the more comprehensive emptiness count
        return combined_empty_count
        
    def diagnose_file(self, output_to_file=False):
        """
        Diagnoses issues with the Excel file and provides detailed information.
        Useful for debugging when things aren't working as expected.
        
        Args:
            output_to_file (bool): If True, writes output to a diagnose.txt file
        """
        output_lines = []
        def log(msg):
            output_lines.append(msg)
            print(msg)
        
        log(f"\n===== DIAGNOSTICS FOR {self.file_path} =====")
        log(f"File exists: {os.path.exists(self.file_path)}")
        if os.path.exists(self.file_path):
            log(f"File size: {os.path.getsize(self.file_path)} bytes")
            log(f"Last modified: {time.ctime(os.path.getmtime(self.file_path))}")
            
            # Try to detect Excel file version
            try:
                import struct
                with open(self.file_path, 'rb') as file:
                    header = file.read(8)
                    if header[:2] == b'\xD0\xCF':  # OLE2 Compound Document (Excel 97-2003)
                        log("Excel format: Excel 97-2003 (.xls)")
                    elif header[:2] == b'PK':  # ZIP file (Excel 2007+)
                        log("Excel format: Excel 2007+ (.xlsx)")
                    else:
                        log(f"Unknown Excel format, header bytes: {header[:8].hex()}")
            except Exception as e:
                log(f"Error detecting Excel format: {str(e)}")
        
        log(f"\nDataFrame information:")
        log(f"Total rows: {len(self.df)}")
        log(f"Columns: {', '.join(self.df.columns.tolist())}")
        
        # Check for duplicate column names
        dupes = [item for item, count in pd.Series(self.df.columns).value_counts().items() if count > 1]
        if dupes:
            log(f"WARNING: Duplicate column names detected: {dupes}")
        
        # Analyze data types
        log("\nColumn data types:")
        for col, dtype in self.df.dtypes.items():
            log(f"  {col}: {dtype}")
        
        if 'label' in self.df.columns:
            log(f"\nLabel column analysis:")
            log(f"NaN values: {self.df['label'].isna().sum()}")
            log(f"Empty strings: {(self.df['label'] == '').sum() if self.df['label'].dtype == 'object' else 0}")
            
        if 'justification' in self.df.columns:
            log(f"\nJustification column analysis:")
            log(f"NaN values: {self.df['justification'].isna().sum()}")
            log(f"Empty strings: {(self.df['justification'] == '').sum() if self.df['justification'].dtype == 'object' else 0}")
        
        # Sample data for inspection
        log("\nSample data (first 3 rows):")
        try:
            sample_data = self.df.head(3).to_string()
            log(sample_data)
        except Exception as e:
            log(f"Error getting sample data: {str(e)}")
        
        log("\n===== END OF DIAGNOSTICS =====\n")
        
        if output_to_file:
            with open("diagnose.txt", "w") as f:
                f.write("\n".join(output_lines))
            print(f"Diagnostic information written to diagnose.txt")
            
    def repair_excel_file(self, backup=True):
        """
        Attempts to repair common Excel file issues.
        
        Args:
            backup (bool): If True, creates a backup of the original file
            
        Returns:
            bool: True if repair was successful, False otherwise
        """
        if not os.path.exists(self.file_path):
            print(f"File not found: {self.file_path}")
            return False
            
        if backup:
            backup_path = f"{self.file_path}.backup"
            import shutil
            try:
                shutil.copy2(self.file_path, backup_path)
                print(f"Backup created at: {backup_path}")
            except Exception as e:
                print(f"Warning: Failed to create backup: {str(e)}")
                return False
        
        # Attempt to load and save the file to fix corruption
        try:
            print(f"Attempting to repair {self.file_path}")
            # Release current DataFrame if exists
            if hasattr(self, 'df'):
                self.df = None
                
            # Load the file using pandas
            temp_df = pd.read_excel(self.file_path)
            
            # Save it back with optimized settings
            temp_df.to_excel(self.file_path, index=False, engine='openpyxl')
            
            # Reload our dataframe
            self.df = pd.read_excel(self.file_path)
            print(f"File repair attempted successfully. Re-loaded {len(self.df)} rows.")
            return True
        except Exception as e:
            print(f"Error during file repair: {str(e)}")
            return False
    
    def close(self):
        """
        Releases resources from the DataHandler.
        Call this method when done with the DataHandler instance.
        """
        # Set DataFrame to None to remove references
        if hasattr(self, 'df'):
            self.df = None
            
        print("DataHandler resources released.")