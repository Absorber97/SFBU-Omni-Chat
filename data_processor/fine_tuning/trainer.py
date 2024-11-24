import openai
from openai import OpenAI
from typing import Dict, Any, List, Optional, Tuple
import os
from config import OPENAI_MODELS, MODEL_PARAMS, get_fine_tuned_model_name
from utils.batch_processor import BatchProcessor
from dataclasses import dataclass

@dataclass
class TrainingFiles:
    """Data class to hold training and validation file information"""
    train_file: str
    val_file: Optional[str] = None
    train_file_id: Optional[str] = None
    val_file_id: Optional[str] = None

class ModelTrainer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.batch_processor = BatchProcessor[str, Dict[str, Any]](
            batch_size=10,
            max_workers=3
        )

    def _get_validation_file(self, train_file_path: str) -> Optional[str]:
        """Get validation file path from training file path"""
        base_path = train_file_path.replace('_train.jsonl', '')
        val_path = f"{base_path}_val.jsonl"
        return val_path if os.path.exists(val_path) else None

    def _upload_file(self, file_path: str, purpose: str = 'fine-tune') -> str:
        """Upload file to OpenAI"""
        with open(file_path, 'rb') as file:
            response = self.client.files.create(
                file=file,
                purpose=purpose
            )
        return response.id

    def _prepare_training_files(self, train_file_path: str) -> TrainingFiles:
        """Prepare and upload training and validation files"""
        training_files = TrainingFiles(train_file=train_file_path)
        
        # Upload training file
        training_files.train_file_id = self._upload_file(train_file_path)
        
        # Check for and upload validation file if exists
        val_file = self._get_validation_file(train_file_path)
        if val_file:
            training_files.val_file = val_file
            training_files.val_file_id = self._upload_file(val_file)
            
        return training_files

    def start_fine_tuning(self, file_path: str, base_model: str = None) -> Dict[str, Any]:
        """Start fine-tuning process with training and validation data"""
        try:
            # Prepare files
            training_files = self._prepare_training_files(file_path)
            
            # Use provided base model or default from config
            model = base_model or OPENAI_MODELS['trainer']
            
            # Create fine-tuning job
            job_params = {
                'training_file': training_files.train_file_id,
                'model': model,
                'suffix': get_fine_tuned_model_name(),
                'hyperparameters': {
                    'n_epochs': MODEL_PARAMS['trainer'].get('n_epochs', 3)
                }
            }
            
            # Add validation file if available
            if training_files.val_file_id:
                job_params['validation_file'] = training_files.val_file_id
            
            # Create the job
            job = self.client.fine_tuning.jobs.create(**job_params)
            
            return {
                'status': 'started',
                'job_id': job.id,
                'train_file_id': training_files.train_file_id,
                'val_file_id': training_files.val_file_id,
                'file_path': file_path,
                'base_model': model,
                'model_name': job.fine_tuned_model
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'file_path': file_path
            }

    def check_status(self, job_id: str) -> Dict[str, Any]:
        """Check status of fine-tuning job with detailed metrics"""
        try:
            job = self.client.fine_tuning.jobs.retrieve(job_id)
            
            # Get training metrics if available
            metrics = {
                'training_loss': None,
                'validation_loss': None
            }
            
            if hasattr(job, 'metrics'):
                metrics.update(job.metrics)
            
            return {
                'status': job.status,
                'fine_tuned_model': job.fine_tuned_model,
                'training_file': job.training_file,
                'validation_file': getattr(job, 'validation_file', None),
                'finished_at': job.finished_at,
                'metrics': metrics
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            } 