from openai import OpenAI
from typing import List, Dict, Tuple, Iterator
import hashlib
import os
import logging
from datetime import datetime
import json
from config import OPENAI_MODELS, MODEL_PARAMS
from itertools import islice
from urllib.parse import urlparse

class JSONLFormatter:
    def __init__(self, output_dir: str = "training_data", api_key: str = None, batch_size: int = 5, source_tracker=None):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.current_output_dir = None
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.batch_size = batch_size
        self.processed_hashes = self._load_existing_hashes()
        self.source_tracker = source_tracker
    
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

    def _generate_qa_pairs_batch(self, batch: List[Dict[str, str]]) -> List[List[Tuple[str, str]]]:
        """Generate Q&A pairs for a batch of items"""
        try:
            messages = []
            for item in batch:
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
            
            # Create batch request
            responses = self.client.chat.completions.create(
                model=OPENAI_MODELS['formatter'],
                messages=messages,
                **MODEL_PARAMS['formatter']
            )
            
            qa_pairs_list = []
            for response in responses.choices:
                qa_text = response.message.content
                qa_pairs = []
                
                for line in qa_text.strip().split('\n'):
                    if '|||' in line:
                        q, a = line.split('|||')
                        qa_pairs.append((
                            self._clean_qa_text(q.strip()),
                            self._clean_qa_text(a.strip())
                        ))
                
                qa_pairs_list.append(qa_pairs)
            
            return qa_pairs_list
            
        except Exception as e:
            self.logger.error(f"OpenAI API batch error: {str(e)}")
            return [[] for _ in batch]  # Return empty lists for failed batch

    def format_data(self, extracted_data: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Format extracted data into JSONL format"""
        formatted_data = []
        source_metadata = {
            "timestamp": datetime.now().strftime('%Y%m%d_%H%M%S'),
            "sources": {
                "original": [],
                "friendly": []
            }
        }
        
        try:
            for data in extracted_data:
                if not data:
                    continue
                    
                url = data.get('url', '')
                title = data.get('title', '')
                content = data.get('content', [])
                
                if not content:
                    continue
                    
                # Add source to metadata if not already added
                if url and url not in source_metadata["sources"]["original"]:
                    source_metadata["sources"]["original"].append(url)
                    friendly_name = self.source_tracker.format_source_path(url)
                    # Remove domain prefix for friendly names
                    if friendly_name.startswith(('sfbu.edu/', 'www.sfbu.edu/')):
                        friendly_name = friendly_name.split('/', 1)[1]
                    source_metadata["sources"]["friendly"].append(friendly_name)
                
                # Format content into Q&A pairs
                for item in content:
                    if isinstance(item, dict) and item.get('text'):
                        context = f"{title} - {item.get('section', 'main')}" if title else item.get('section', 'main')
                        text = item['text']
                        
                        # Generate Q&A pairs for this content
                        qa_pairs = self._generate_qa_pairs(text, context)
                        formatted_data.extend(qa_pairs)
            
            # Update metadata counts
            total_examples = len(formatted_data)
            train_size = int(total_examples * 0.8)  # 80% for training
            
            # Add counts to metadata
            source_metadata.update({
                "total_examples": total_examples,
                "train_examples": train_size,
                "val_examples": total_examples - train_size
            })
            
            return formatted_data, source_metadata
            
        except Exception as e:
            self.logger.error(f"Error formatting data: {str(e)}")
            raise

    def _get_friendly_source_name(self, source_path: str) -> str:
        """Convert source path to user-friendly name"""
        try:
            # Check if it's a URL
            if source_path.startswith(('http://', 'https://')):
                parsed = urlparse(source_path)
                path = parsed.path.strip('/')
                if not path:
                    return parsed.netloc.split('.')[0].capitalize()
                
                # Split path and take meaningful segments
                segments = path.split('/')
                meaningful_segments = [
                    seg for seg in segments 
                    if seg and not seg.isdigit() and seg not in {'index', 'html', 'php'}
                ]
                
                # Convert to title case and join with spaces
                friendly_name = ' '.join(
                    word.capitalize() 
                    for segment in meaningful_segments 
                    for word in segment.split('-')
                )
                return friendly_name
                
            # Handle file paths (existing logic)
            filename = os.path.splitext(os.path.basename(source_path))[0]
            if filename.endswith('-web'):
                filename = filename[:-4]
            friendly_name = filename.replace('-', ' ').replace('_', ' ')
            return ' '.join(word.capitalize() for word in friendly_name.split())
                
        except Exception:
            return source_path

    def save_jsonl(self, formatted_data: List[Dict[str, str]], dataset_name: str, source_metadata: Dict[str, str]) -> Dict[str, str]:
        """Save formatted data to JSONL files with enhanced metadata"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join(self.output_dir, timestamp)
        os.makedirs(output_dir, exist_ok=True)
        self.current_output_dir = output_dir
        
        # Format filenames
        train_file = os.path.join(output_dir, f"{dataset_name}_train.jsonl")
        val_file = os.path.join(output_dir, f"{dataset_name}_val.jsonl")
        metadata_file = os.path.join(output_dir, f"{dataset_name}_metadata.json")
        
        # Split data (90/10)
        split_idx = int(len(formatted_data) * 0.9)
        train_data = formatted_data[:split_idx]
        val_data = formatted_data[split_idx:]
        
        # Save files
        self._save_jsonl_file(train_data, train_file)
        self._save_jsonl_file(val_data, val_file)
        
        # Enhanced metadata
        metadata = source_metadata
        
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            'train_file': train_file,
            'val_file': val_file,
            'metadata_file': metadata_file,
            'output_dir': output_dir
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

    def _generate_qa_pairs(self, text: str, context: str = "") -> List[Dict[str, str]]:
        """Generate Q&A pairs from text using OpenAI API"""
        try:
            # Clean the input text
            text = self._clean_qa_text(text)
            if len(text) < 50:  # Skip very short texts
                return []

            # Prepare the prompt
            system_prompt = """
            Generate 2-3 contextually relevant question-answer pairs from the given text.
            Requirements:
            - Focus on important information useful for students or staff
            - Questions should be clear and direct
            - Answers should be complete sentences
            - Avoid redundant or trivial questions
            - Each pair should be on a new line in format: Q: [question] | A: [answer]
            """

            # Remove potentially conflicting parameters from MODEL_PARAMS
            model_params = MODEL_PARAMS['formatter'].copy()
            params_to_remove = ['temperature', 'max_tokens']  # Add any other potentially conflicting params
            for param in params_to_remove:
                model_params.pop(param, None)
            
            # Make API call with clean parameters
            response = self.client.chat.completions.create(
                model=OPENAI_MODELS['formatter'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context: {context}\nText: {text}"}
                ],
                temperature=0.7,
                max_tokens=1000,
                **model_params
            )

            # Parse response
            qa_text = response.choices[0].message.content
            qa_pairs = []

            # Process each line
            for line in qa_text.strip().split('\n'):
                if '|' in line:
                    q_part, a_part = line.split('|')
                    question = q_part.replace('Q:', '').strip()
                    answer = a_part.replace('A:', '').strip()
                    
                    # Generate hash for deduplication
                    content_hash = self._generate_hash(question + answer)
                    
                    if content_hash not in self.processed_hashes:
                        self.processed_hashes.add(content_hash)
                        qa_pairs.append({
                            "prompt": question,
                            "completion": answer
                        })

            return qa_pairs

        except Exception as e:
            self.logger.error(f"Error generating Q&A pairs: {str(e)}")
            return []