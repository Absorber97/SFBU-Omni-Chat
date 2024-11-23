import logging
import queue
from typing import Optional
from datetime import datetime
import os

class QueueHandler(logging.Handler):
    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue
        
    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_queue.put(msg)
        except Exception:
            self.handleError(record)

class RealTimeLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)  # Set default level
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        
        # Configure formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.queue_handler.setFormatter(formatter)
        self.logger.addHandler(self.queue_handler)
        
        # Set up file handler only when needed
        self.file_handler: Optional[logging.FileHandler] = None
    
    def setup_file_handler(self, log_dir: str):
        """Set up file handler only when logging actually occurs"""
        if not self.file_handler:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(
                log_dir, 
                f"sfbu_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )
            self.file_handler = logging.FileHandler(log_file)
            self.file_handler.setFormatter(self.queue_handler.formatter)
            self.logger.addHandler(self.file_handler)
    
    def get_logs(self) -> str:
        """Get all logs from queue"""
        logs = []
        while not self.log_queue.empty():
            logs.append(self.log_queue.get())
        return '\n'.join(logs)
    
    # Add logging method proxies
    def info(self, msg: str):
        """Log info message"""
        self.logger.info(msg)
    
    def error(self, msg: str):
        """Log error message"""
        self.logger.error(msg)
    
    def warning(self, msg: str):
        """Log warning message"""
        self.logger.warning(msg)
    
    def debug(self, msg: str):
        """Log debug message"""
        self.logger.debug(msg)