import openai
from openai import OpenAI
from typing import Dict, Any, List
import time
from config import OPENAI_MODELS, MODEL_PARAMS
from utils.batch_processor import BatchProcessor

class ModelTrainer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.batch_processor = BatchProcessor[str, Dict[str, Any]](
            batch_size=10,
            max_workers=3
        )
        
    def start_fine_tuning_batch(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Start fine-tuning for multiple files"""
        def process_batch(batch: List[str]) -> List[Dict[str, Any]]:
            results = []
            for file_path in batch:
                try:
                    with open(file_path, 'rb') as file:
                        response = self.client.files.create(
                            file=file,
                            purpose='fine-tune'
                        )
                    file_id = response.id
                    
                    job = self.client.fine_tuning.jobs.create(
                        training_file=file_id,
                        model=OPENAI_MODELS['trainer']
                    )
                    
                    results.append({
                        'status': 'started',
                        'job_id': job.id,
                        'file_id': file_id,
                        'file_path': file_path
                    })
                except Exception as e:
                    results.append({
                        'status': 'error',
                        'error': str(e),
                        'file_path': file_path
                    })
            return results
            
        return self.batch_processor.process_batch(file_paths, process_batch)
    
    def check_status(self, job_id: str) -> Dict[str, Any]:
        """Check status of fine-tuning job"""
        try:
            job = self.client.fine_tuning.jobs.retrieve(job_id)
            return {
                'status': job.status,
                'fine_tuned_model': job.fine_tuned_model,
                'training_file': job.training_file,
                'finished_at': job.finished_at
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            } 