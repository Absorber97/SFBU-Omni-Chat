import logging
from typing import List
from queue import Queue
from datetime import datetime

class QueueHandler(logging.Handler):
    def __init__(self, log_queue: Queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_queue.put(msg)
        except Exception:
            self.handleError(record)

class Logger:
    def __init__(self):
        self.logger = logging.getLogger('SFBUApp')
        self.logger.setLevel(logging.INFO)
        
        # Create formatters and handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S,%f'
        )
        
        # Queue for storing logs
        self.log_queue = Queue()
        queue_handler = QueueHandler(self.log_queue)
        queue_handler.setFormatter(formatter)
        
        # File handler
        file_handler = logging.FileHandler('app.log')
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(queue_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def get_logs(self) -> str:
        """Get all logs from queue"""
        logs = []
        while not self.log_queue.empty():
            logs.append(self.log_queue.get())
        return '\n'.join(logs) 