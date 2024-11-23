from data_processor.extractors.pdf_extractor import PDFExtractor
from data_processor.extractors.url_extractor import URLExtractor
from data_processor.formatters.jsonl_formatter import JSONLFormatter
from data_processor.fine_tuning.trainer import ModelTrainer
from chat_interface.chat_manager import ChatManager
from config import OPENAI_API_KEY
from utils.logging_handler import RealTimeLogger
from typing import Optional, Dict, List
import os
import json
from datetime import datetime

class SFBUApp:
    def __init__(self):
        self.logger = RealTimeLogger(__name__)
        self.pdf_extractor = PDFExtractor()
        self.url_extractor = URLExtractor()
        self.jsonl_formatter = JSONLFormatter(
            output_dir="training_data",
            api_key=os.getenv('OPENAI_API_KEY'),
            batch_size=5
        )
        
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.trainer = ModelTrainer(api_key=OPENAI_API_KEY)
        self.chat_manager: Optional[ChatManager] = None

    def _load_preview_data(self, train_file: str, val_file: str) -> Dict:
        """Load preview data from JSONL files"""
        preview_limit = 5
        
        def load_jsonl_preview(file_path: str, limit: int) -> List[List]:
            data = []
            try:
                with open(file_path, 'r') as f:
                    for i, line in enumerate(f):
                        if i >= limit:
                            break
                        item = json.loads(line)
                        data.append([item['prompt'], item['completion']])
            except Exception as e:
                self.logger.error(f"Error loading preview data: {str(e)}")
            return data

        return {
            'train_preview': load_jsonl_preview(train_file, preview_limit),
            'val_preview': load_jsonl_preview(val_file, preview_limit)
        } 