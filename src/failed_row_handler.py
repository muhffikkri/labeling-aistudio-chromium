# src/failed_row_handler.py
import pandas as pd
import os

class FailedRowHandler:
    def __init__(self, file_path="data/failed_labeled.xlsx"):
        """
        Initializes the handler for rows that fail validation.
        
        Args:
            file_path (str): The path to store the failed rows Excel file.
        """
        self.file_path = file_path
        self.failed_rows = []

    def add_failed_row(self, original_text: str, invalid_label: str, justification: str, reason: str):
        """
        Adds a failed row to the internal list.
        
        Args:
            original_text (str): The original 'full_text' that was processed.
            invalid_label (str): The invalid label received from the AI.
            justification (str): The justification received.
            reason (str): The reason for the failure (e.g., "Invalid Label").
        """
        self.failed_rows.append({
            "full_text": original_text,
            "invalid_label": invalid_label,
            "justification": justification,
            "failure_reason": reason
        })
        print(f"Logged a failed row. Reason: {reason}. Invalid Label: '{invalid_label}'")

    def save_to_file(self):
        """
        Saves all collected failed rows to an Excel file.
        Appends to the file if it already exists.
        """
        if not self.failed_rows:
            print("No failed rows to save.")
            return

        new_failures_df = pd.DataFrame(self.failed_rows)

        if os.path.exists(self.file_path):
            print(f"Appending {len(new_failures_df)} rows to existing failed log: {self.file_path}")
            existing_df = pd.read_excel(self.file_path)
            combined_df = pd.concat([existing_df, new_failures_df], ignore_index=True)
        else:
            print(f"Creating new failed log with {len(new_failures_df)} rows: {self.file_path}")
            combined_df = new_failures_df

        combined_df.to_excel(self.file_path, index=False)
        print("Failed rows saved successfully.")
        
        # Clear the list after saving
        self.failed_rows = []