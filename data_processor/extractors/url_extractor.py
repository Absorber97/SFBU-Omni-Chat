import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from urllib.parse import urljoin

class URLExtractor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def extract_text(self, url: str, allowed_domains: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """Extract text content from URLs"""
        try:
            self.logger.info(f"Starting extraction from URL: {url}")
            extracted_data = []
            
            # Use empty list if allowed_domains is None
            allowed_domains = allowed_domains or []
            
            # Fetch and parse the webpage
            response = requests.get(url, headers={'User-Agent': 'SFBU-Bot'})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract main content (customize selectors based on SFBU website structure)
            main_content = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
            
            current_section = ""
            current_text = []
            
            for element in main_content:
                if element.name.startswith('h'):
                    # Save previous section if exists
                    if current_text:
                        extracted_data.append({
                            'content': ' '.join(current_text),
                            'section': current_section,
                            'source': url
                        })
                    current_section = element.get_text().strip()
                    current_text = []
                else:
                    text = element.get_text().strip()
                    if text:
                        current_text.append(text)
            
            # Add the last section
            if current_text:
                extracted_data.append({
                    'content': ' '.join(current_text),
                    'section': current_section,
                    'source': url
                })
            
            self.logger.info(f"Successfully extracted {len(extracted_data)} sections from {url}")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error extracting from URL {url}: {str(e)}")
            raise 