# src/logger.py
import sys
import os
import datetime

class Logger:
    def __init__(self, log_dir="logs"):
        """
        Initializes the Logger to redirect stdout and stderr to a log file.
        """
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"automation_log_{timestamp}.log"
        self.log_filepath = os.path.join(log_dir, log_filename)

        self.terminal = sys.stdout
        self.log_file = open(self.log_filepath, "w", encoding='utf-8')

        sys.stdout = self
        sys.stderr = self
        
        print(f"Logging output to: {self.log_filepath}")

    def write(self, message):
        """
        Writes the message to both the terminal and the log file.
        """
        self.terminal.write(message)
        self.log_file.write(message)
        self.flush()

    def flush(self):
        """
        Flushes the streams to ensure data is written.
        """
        self.terminal.flush()
        self.log_file.flush()

    def close(self):
        """
        Restores the original stdout and stderr and closes the log file.
        """
        sys.stdout = self.terminal
        sys.stderr = self.terminal
        self.log_file.close()