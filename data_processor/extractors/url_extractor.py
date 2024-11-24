import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .url_processor import URLProcessor, URLProcessingConfig
import logging

class URLExtractor:
    def __init__(self):
        self.processor = URLProcessor()
        self.logger = logging.getLogger(__name__)
    
    def extract_text(self, url: str, enable_recursion: bool = False, max_urls: int = 2) -> List[Dict[str, str]]:
        """Extract text from URL with optional recursion"""
        try:
            # Configure processor
            self.processor.config.recursion_enabled = enable_recursion
            self.processor.config.max_links_per_page = max_urls if enable_recursion else 0
            
            # Process URL
            return self.processor.process_with_recursion(url)
        except Exception as e:
            self.logger.error(f"Error extracting text from URL {url}: {str(e)}")
            return []