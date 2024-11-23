import openai
from openai import OpenAI
from typing import Dict, Any
import time

class ModelTrainer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def start_fine_tuning(self, training_file_path: str) -> Dict[str, Any]:
        """Start fine-tuning process with OpenAI"""
        try:
            # Upload the training file
            with open(training_file_path, 'rb') as file:
                response = self.client.files.create(
                    file=file,
                    purpose='fine-tune'
                )
            file_id = response.id
            
            # Create fine-tuning job
            job = self.client.fine_tuning.jobs.create(
                training_file=file_id,
                model="gpt-3.5-turbo"  # Updated to supported model
            )
            
            # Track the source
            from data_processor.source_tracker import SourceTracker
            tracker = SourceTracker()
            tracker.add_fine_tuned_source({
                'file_path': training_file_path,
                'job_id': job.id,
                'file_id': file_id,
                'status': 'started'
            })
            
            return {
                'status': 'started',
                'job_id': job.id,
                'file_id': file_id
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
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