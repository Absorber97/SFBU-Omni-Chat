import PyPDF2
from typing import List, Dict
import spacy
import re
import os

class PDFExtractor:
    def __init__(self):
        # Load spaCy model for text processing
        self.nlp = spacy.load("en_core_web_sm")
        
    def extract_text(self, pdf_path: str) -> List[Dict]:
        """Extract text from PDF with meaningful context preservation"""
        extracted_data = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # First pass: Identify section headers and structure
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                cleaned_text = self._clean_text(text)
                
                # Process text to identify sections
                doc = self.nlp(cleaned_text)
                
                current_section = f"Page {page_num + 1}"
                section_content = []
                
                for sent in doc.sents:
                    if self._is_section_header(sent.text):
                        # If we have content from previous section, process it
                        if section_content:
                            # Split content into smaller chunks for better Q&A generation
                            chunks = self._split_into_chunks(' '.join(section_content))
                            for chunk in chunks:
                                if self._is_meaningful_chunk(chunk):
                                    extracted_data.append({
                                        'url': pdf_path,
                                        'title': os.path.basename(pdf_path).replace('.pdf', ''),
                                        'content': [{
                                            'text': chunk,
                                            'section': current_section,
                                            'type': 'text'
                                        }]
                                    })
                            section_content = []
                        current_section = sent.text.strip()
                    else:
                        # Add content to current section if it's meaningful
                        if self._is_meaningful_content(sent.text):
                            section_content.append(sent.text.strip())
                
                # Process the last section of the page
                if section_content:
                    chunks = self._split_into_chunks(' '.join(section_content))
                    for chunk in chunks:
                        if self._is_meaningful_chunk(chunk):
                            extracted_data.append({
                                'url': pdf_path,
                                'title': os.path.basename(pdf_path).replace('.pdf', ''),
                                'content': [{
                                    'text': chunk,
                                    'section': current_section,
                                    'type': 'text'
                                }]
                            })
        
        return extracted_data
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text while preserving meaningful punctuation"""
        # Remove extra whitespace while preserving sentence boundaries
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep meaningful punctuation
        text = re.sub(r'[^\w\s.,?!;:()\-"]', '', text)
        # Fix common OCR issues
        text = self._fix_ocr_artifacts(text)
        return text.strip()
    
    def _fix_ocr_artifacts(self, text: str) -> str:
        """Fix common OCR artifacts and improve text quality"""
        # Fix common OCR mistakes
        fixes = {
            r'(?<=\w)\.(?=\w)': '. ',  # Add space after period between words
            r'(?<=\d),(?=\d)': '',     # Remove comma between numbers
            r'\b([A-Z])\s+(?=[a-z])': r'\1',  # Fix split words
        }
        
        for pattern, replacement in fixes.items():
            text = re.sub(pattern, replacement, text)
        return text
    
    def _is_section_header(self, text: str) -> bool:
        """Identify if text is likely a section header"""
        # Characteristics of section headers:
        # 1. Short length
        # 2. Often starts with numbers (e.g., "1.2 Section Name")
        # 3. Often in Title Case
        # 4. No ending punctuation except for colons
        text = text.strip()
        return (
            len(text.split()) <= 7 and
            (text[0].isupper() or text[0].isdigit()) and
            not any(text.endswith(p) for p in '.!?') and
            (text.istitle() or bool(re.match(r'\d+\.?\d*\s+[A-Z]', text)))
        )
    
    def _is_meaningful_content(self, text: str) -> bool:
        """Check if the text contains meaningful content"""
        text = text.strip()
        # Filter out empty lines, single words, and purely numerical content
        return (
            len(text) > 0 and
            len(text.split()) > 3 and
            not text.isdigit() and
            not all(c.isdigit() or c.isspace() or c in '.,:-' for c in text)
        )
    
    def _split_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better context preservation"""
        words = text.split()
        chunks = []
        
        if len(words) <= chunk_size:
            return [text]
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def _is_meaningful_chunk(self, text: str) -> bool:
        """Check if a chunk contains enough meaningful content"""
        text = text.strip()
        # More detailed content validation
        return (
            len(text) >= 200 and  # Minimum length for good context
            len(text.split()) >= 30 and  # Minimum word count
            not text.isdigit() and
            not all(c.isdigit() or c.isspace() or c in '.,:-' for c in text) and
            sum(1 for c in text if c.isalpha()) / len(text) > 0.5  # At least 50% letters
        )