from openai import OpenAI
from typing import List, Dict, Tuple, Iterator
import hashlib
import os
import logging
from datetime import datetime
import json
from config import OPENAI_MODELS, MODEL_PARAMS
from itertools import islice

class JSONLFormatter:
    def __init__(self, output_dir: str = "training_data", api_key: str = None, batch_size: int = 5):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.current_output_dir = None
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.batch_size = batch_size
        # Load existing hashes from all training data
        self.processed_hashes = self._load_existing_hashes()
    
    def _load_existing_hashes(self) -> set:
        """Load hashes from all existing training data"""
        hashes = set()
        if os.path.exists(self.output_dir):
            for timestamp_dir in os.listdir(self.output_dir):
                dir_path = os.path.join(self.output_dir, timestamp_dir)
                if os.path.isdir(dir_path):
                    for file in os.listdir(dir_path):
                        if file.endswith('.jsonl'):
                            file_path = os.path.join(dir_path, file)
                            with open(file_path, 'r') as f:
                                for line in f:
                                    data = json.loads(line)
                                    content_hash = self._generate_hash(
                                        data['prompt'] + data['completion']
                                    )
                                    hashes.add(content_hash)
        return hashes

    def _batch_items(self, items: List[Dict[str, str]], batch_size: int) -> List[List[Dict[str, str]]]:
        """Split items into batches"""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]

    def format_data(self, data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format extracted data into JSONL format with preview updates"""
        formatted_data = []
        
        # Process in batches using self.batch_size
        for batch in self._batch_items(data, self.batch_size):
            try:
                qa_pairs = self._generate_qa_pairs_batch(batch)
                
                for item, pairs in zip(batch, qa_pairs):
                    for prompt, completion in pairs:
                        # Clean both prompt and completion
                        clean_prompt = self._clean_qa_text(prompt)
                        clean_completion = self._clean_qa_text(completion)
                        
                        content_hash = self._generate_hash(clean_prompt + clean_completion)
                        
                        if content_hash not in self.processed_hashes:
                            entry = {
                                'prompt': clean_prompt,
                                'completion': clean_completion,
                                'source': item['source'],
                                'section': item['section'],
                                'page': item.get('page', '')
                            }
                            formatted_data.append(entry)
                            self.processed_hashes.add(content_hash)
                            
                            # Update preview immediately
                            self._update_preview(entry)
                            
            except Exception as e:
                self.logger.error(f"Error processing batch: {str(e)}")
                continue
                
        return formatted_data

    def _generate_qa_pairs_batch(self, items: List[Dict[str, str]]) -> List[List[Tuple[str, str]]]:
        """Generate Q&A pairs for a batch of items"""
        try:
            # Prepare batch messages
            messages = []
            for item in items:
                messages.append([
                    {"role": "system", "content": """
                    Generate 2-3 contextually relevant question-answer pairs from the given text.
                    Requirements:
                    - Focus on important information useful for students or staff
                    - Questions should be clear and direct (no "Q:" prefix)
                    - Answers should be complete sentences (no "A:" prefix)
                    - Avoid redundant or trivial questions
                    - Make questions natural and conversational
                    
                    Format: Return only the Q&A pairs, one per line, separated by ||| between question and answer.
                    Example:
                    What are the housing options available at SFBU? ||| SFBU offers non-traditional campus housing for both undergraduate and graduate students.
                    How do I contact the Residential Life staff? ||| You can reach the Residential Life staff through email at residentiallife@sfbu.edu.
                    """},
                    {"role": "user", "content": f"Section: {item['section']}\n\nContent: {item['content']}"}
                ])

            # Create batch completion request
            responses = []
            for msg in messages:
                response = self.client.chat.completions.create(
                    model=OPENAI_MODELS['formatter'],
                    messages=msg,
                    **MODEL_PARAMS['formatter']
                )
                responses.append(response)

            # Process all responses
            all_qa_pairs = []
            for response in responses:
                qa_text = response.choices[0].message.content
                qa_pairs = []
                
                for line in qa_text.strip().split('\n'):
                    if '|||' in line:
                        q, a = line.split('|||')
                        # Clean up any remaining Q: or A: prefixes
                        q = q.strip().replace('Q:', '').replace('A:', '').strip()
                        a = a.strip().replace('Q:', '').replace('A:', '').strip()
                        qa_pairs.append((q, a))
                
                all_qa_pairs.append(qa_pairs)
            
            return all_qa_pairs
            
        except Exception as e:
            self.logger.error(f"OpenAI API batch error: {str(e)}")
            return [[] for _ in items]  # Return empty lists for failed batch

    def save_jsonl(self, formatted_data: List[Dict[str, str]], dataset_name: str) -> Dict[str, str]:
        """Save formatted data to JSONL files with train/val split"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join(self.output_dir, timestamp)
        os.makedirs(output_dir, exist_ok=True)
        self.current_output_dir = output_dir
        
        # Format filenames
        train_file = os.path.join(output_dir, f"{dataset_name}_train.jsonl")
        val_file = os.path.join(output_dir, f"{dataset_name}_val.jsonl")
        metadata_file = os.path.join(output_dir, f"{dataset_name}_metadata.json")
        
        # Split data into train/val (90/10 split)
        split_idx = int(len(formatted_data) * 0.9)
        train_data = formatted_data[:split_idx]
        val_data = formatted_data[split_idx:]
        
        # Clean up source paths before saving (keep extension)
        for data in [train_data, val_data]:
            for item in data:
                if 'source' in item:
                    item['source'] = os.path.basename(item['source'])  # Keep the extension
        
        # Save files
        self._save_jsonl_file(train_data, train_file)
        self._save_jsonl_file(val_data, val_file)
        
        # Save metadata
        metadata = {
            'timestamp': timestamp,
            'total_examples': len(formatted_data),
            'train_examples': len(train_data),
            'val_examples': len(val_data),
            'sources': list(set(os.path.basename(item['source']) for item in formatted_data))
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            'train_file': train_file,
            'val_file': val_file,
            'metadata_file': metadata_file
        }

    def _save_jsonl_file(self, data: List[Dict], file_path: str):
        """Save data to JSONL file"""
        with open(file_path, 'w') as f:
            for item in data:
                f.write(json.dumps(item) + '\n')

    def _generate_hash(self, content: str) -> str:
        """Generate hash for deduplication"""
        return hashlib.md5(content.encode()).hexdigest() 

    def _clean_qa_text(self, text: str) -> str:
        """Clean up text and handle special characters"""
        # Replace problematic characters with safe alternatives
        replacements = {
            '"': '"',  # Smart quotes
            '"': '"',
            ''': "'",
            ''': "'",
            '…': '...',
            '–': '-',
            '—': '-',
            '\u2028': ' ',  # Line separator
            '\u2029': ' ',  # Paragraph separator
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        # Remove any other control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _update_preview(self, entry: Dict[str, str]):
        """Update preview data"""
        # Implement preview update mechanism
        # This will be called by the Gradio interface
        pass