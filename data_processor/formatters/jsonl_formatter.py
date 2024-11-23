import json
from typing import List, Dict
import hashlib
import os
import logging
from datetime import datetime
import spacy

class JSONLFormatter:
    def __init__(self, output_dir: str = "training_data"):
        self.processed_hashes = set()
        self.nlp = spacy.load("en_core_web_sm")
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Create output directory structure
        self._create_directory_structure()
        
    def _create_directory_structure(self):
        """Create directory structure for training data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_output_dir = os.path.join(self.output_dir, timestamp)
        os.makedirs(self.current_output_dir, exist_ok=True)
        
    def format_data(self, extracted_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format extracted data into Q&A pairs"""
        self.logger.info("Starting data formatting")
        formatted_data = []
        
        for item in extracted_data:
            # Process content using spaCy for better context understanding
            doc = self.nlp(item['content'])
            
            # Generate different types of Q&A pairs
            qa_pairs = []
            qa_pairs.extend(self._generate_definition_pairs(doc))
            qa_pairs.extend(self._generate_information_pairs(doc))
            
            for prompt, completion in qa_pairs:
                content_hash = self._generate_hash(prompt + completion)
                
                if content_hash not in self.processed_hashes:
                    entry = {
                        'prompt': prompt,
                        'completion': completion,
                        'source': item.get('source', ''),
                        'section': item.get('section', ''),
                        'page': item.get('page', '')
                    }
                    formatted_data.append(entry)
                    self.processed_hashes.add(content_hash)
        
        self.logger.info(f"Generated {len(formatted_data)} Q&A pairs")
        return formatted_data
    
    def save_jsonl(self, formatted_data: List[Dict[str, str]], dataset_name: str, train_ratio: float = 0.8):
        """Save formatted data with proper organization and train/validation split"""
        # Calculate split indices
        total_samples = len(formatted_data)
        train_size = int(total_samples * train_ratio)
        
        # Randomly shuffle data
        import random
        random.shuffle(formatted_data)
        
        # Split data
        train_data = formatted_data[:train_size]
        val_data = formatted_data[train_size:]
        
        # Save training data
        train_file = os.path.join(self.current_output_dir, f"{dataset_name}_train.jsonl")
        self.logger.info(f"Saving training data ({len(train_data)} samples) to {train_file}")
        self._save_jsonl_file(train_data, train_file)
        
        # Save validation data
        val_file = os.path.join(self.current_output_dir, f"{dataset_name}_val.jsonl")
        self.logger.info(f"Saving validation data ({len(val_data)} samples) to {val_file}")
        self._save_jsonl_file(val_data, val_file)
        
        # Save metadata
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'total_entries': total_samples,
            'train_entries': len(train_data),
            'val_entries': len(val_data),
            'train_ratio': train_ratio,
            'sources': list(set(item['source'] for item in formatted_data)),
            'train_file': os.path.basename(train_file),
            'val_file': os.path.basename(val_file)
        }
        
        metadata_file = os.path.join(self.current_output_dir, f"{dataset_name}_metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            'train_file': train_file,
            'val_file': val_file,
            'metadata_file': metadata_file
        }
    
    def _save_jsonl_file(self, data: List[Dict[str, str]], file_path: str):
        """Helper method to save JSONL file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data:
                json.dump(item, f)
                f.write('\n')
    
    def _generate_definition_pairs(self, doc) -> List[tuple]:
        """Generate definition-style Q&A pairs"""
        pairs = []
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'EVENT', 'LAW']:
                prompt = f"What is {ent.text} at SFBU?"
                # Find the sentence containing this entity
                for sent in doc.sents:
                    if ent.start >= sent.start and ent.end <= sent.end:
                        completion = sent.text
                        pairs.append((prompt, completion))
                        break
        return pairs
    
    def _generate_information_pairs(self, doc) -> List[tuple]:
        """Generate information-seeking Q&A pairs"""
        pairs = []
        for sent in doc.sents:
            # Generate questions based on sentence content
            if any(keyword in sent.text.lower() for keyword in 
                  ['requirement', 'deadline', 'cost', 'fee', 'program', 'course', 'admission']):
                
                text = sent.text.strip()
                if len(text) > 20:  # Ignore very short sentences
                    # Generate different types of questions
                    if 'requirement' in text.lower():
                        prompt = f"What are the requirements for {text.split('requirement')[0].strip()}?"
                    elif 'deadline' in text.lower():
                        prompt = f"What is the deadline for {text.split('deadline')[0].strip()}?"
                    elif any(word in text.lower() for word in ['cost', 'fee']):
                        prompt = f"What is the cost or fee for {text.split('cost')[0].strip()}?"
                    else:
                        prompt = f"Can you provide information about {text.split()[0:3]}?"
                    
                    completion = text
                    pairs.append((prompt, completion))
        
        return pairs
    
    def _generate_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest() 