import PyPDF2
from typing import List, Dict
import spacy
import re

class PDFExtractor:
    def __init__(self):
        # Load spaCy model for text processing
        self.nlp = spacy.load("en_core_web_sm")
        
    def extract_text(self, pdf_path: str) -> List[Dict[str, str]]:
        """
        Extract text from PDF and split into meaningful chunks
        """
        extracted_data = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Process each page
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                # Clean and process text
                cleaned_text = self._clean_text(text)
                chunks = self._split_into_chunks(cleaned_text)
                
                for chunk in chunks:
                    extracted_data.append({
                        'page': page_num + 1,
                        'content': chunk,
                        'source': pdf_path
                    })
                    
        return extracted_data
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters
        text = re.sub(r'[^\w\s.,?!-]', '', text)
        return text.strip()
    
    def _split_into_chunks(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        """Split text into meaningful chunks using spaCy"""
        doc = self.nlp(text)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sent in doc.sents:
            sent_text = sent.text.strip()
            sent_size = len(sent_text)
            
            if current_size + sent_size > max_chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sent_text]
                current_size = sent_size
            else:
                current_chunk.append(sent_text)
                current_size += sent_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks 