import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import spacy
from urllib.parse import urlparse

class URLExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
    
    def _get_meaningful_url_name(self, url: str) -> str:
        """Extract meaningful name from URL"""
        try:
            # Parse URL
            parsed = urlparse(url)
            # Get path without leading/trailing slashes
            path = parsed.path.strip('/')
            
            if not path:
                # If no path, use domain without TLD
                return parsed.netloc.split('.')[0]
            
            # Split path and take meaningful segments
            segments = path.split('/')
            # Filter out common words and join with hyphens
            meaningful_segments = [
                seg for seg in segments 
                if seg and not seg.isdigit() and seg not in {'index', 'html', 'php'}
            ]
            
            return '-'.join(meaningful_segments) if meaningful_segments else parsed.netloc
            
        except Exception:
            return "unknown-source"
    
    def extract_text(self, url: str) -> List[Dict[str, str]]:
        """Extract text from URL with structure preservation"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get meaningful source name
            source_name = f"{self._get_meaningful_url_name(url)}"
            
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
                            'source': f"{source_name}-web",
                            'page': ''  # URLs don't have pages
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
                    'source': f"{source_name}-web",
                    'page': ''
                })
            
            return extracted_data
            
        except Exception as e:
            raise Exception(f"Error extracting text from URL: {str(e)}")