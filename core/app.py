from data_processor.extractors.pdf_extractor import PDFExtractor
from data_processor.extractors.url_extractor import URLExtractor
from data_processor.formatters.jsonl_formatter import JSONLFormatter
from data_processor.source_tracker import SourceTracker
from utils.logger import Logger
from data_processor.fine_tuning.trainer import ModelTrainer
from config import OPENAI_API_KEY
import os
import json
from typing import Dict, List, Optional

class SFBUApp:
    def __init__(self):
        """Initialize the SFBU App with required components"""
        self.logger = Logger()  # Use Logger class directly
        
        # Initialize trainer with API key
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required")
        self.trainer = ModelTrainer(api_key=OPENAI_API_KEY)
        
        # Initialize other components
        self.chat_manager = None  # Will be initialized when needed
        self.source_tracker = SourceTracker()
        self.jsonl_formatter = JSONLFormatter(
            source_tracker=self.source_tracker
        )
        self.pdf_extractor = PDFExtractor()
        self.url_extractor = URLExtractor()
        
    def _load_preview_data(self, train_file: str, val_file: str) -> Dict[str, List[Dict]]:
        """Load preview data from training and validation files"""
        preview_data = {
            'train_preview': [],
            'val_preview': []
        }
        
        try:
            # Load a few examples from train file
            if os.path.exists(train_file):
                with open(train_file, 'r') as f:
                    for i, line in enumerate(f):
                        if i >= 5:  # Only load first 5 examples
                            break
                        preview_data['train_preview'].append(json.loads(line))
                        
            # Load a few examples from val file
            if os.path.exists(val_file):
                with open(val_file, 'r') as f:
                    for i, line in enumerate(f):
                        if i >= 3:  # Only load first 3 examples
                            break
                        preview_data['val_preview'].append(json.loads(line))
                        
        except Exception as e:
            self.logger.error(f"Error loading preview data: {str(e)}")
            
        return preview_data 