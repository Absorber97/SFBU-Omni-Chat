import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import spacy
from urllib.parse import urlparse

class URLExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
    
    def extract_text(self, url: str) -> List[Dict[str, str]]:
        """Extract text from URL with structure preservation"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Use full URL as source
            source_name = url
            
            extracted_data = []
            current_section = ""
            section_content = []
            
            # Process main content areas
            for element in soup.find_all(['h1', 'h2', 'h3', 'p']):
                if element.name in ['h1', 'h2', 'h3']:
                    # Save previous section if exists
                    if section_content:
                        extracted_data.append({
                            'section': current_section,
                            'content': ' '.join(section_content),
                            'source': source_name,  # Use full URL
                            'page': ''
                        })
                        section_content = []
                    current_section = element.get_text().strip()
                elif element.name == 'p':
                    text = element.get_text().strip()
                    if text:  # Only add non-empty paragraphs
                        section_content.append(text)
            
            # Add final section
            if section_content:
                extracted_data.append({
                    'section': current_section,
                    'content': ' '.join(section_content),
                    'source': source_name,  # Use full URL
                    'page': ''
                })
            
            return extracted_data
            
        except Exception as e:
            raise Exception(f"Error extracting text from URL: {str(e)}")