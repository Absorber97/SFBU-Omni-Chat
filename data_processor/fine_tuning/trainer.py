import openai
from openai import OpenAI
from typing import Dict, Any, List, Optional, Tuple
import os
import logging
from dataclasses import dataclass
from config import (
    OPENAI_MODELS, 
    MODEL_PARAMS, 
    MODEL_CONFIG, 
    get_fine_tuned_model_name
)
from utils.batch_processor import BatchProcessor

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
        self.logger = logging.getLogger(__name__)
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
                'suffix': MODEL_CONFIG['fine_tuned_suffix'],
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

    def get_available_models(self) -> List[str]:
        """Fetch available models for fine-tuning"""
        try:
            models = self.client.models.list()
            
            # Get our fine-tuning suffix from config
            suffix = MODEL_CONFIG['fine_tuned_suffix']
            base_name = MODEL_CONFIG['base_name']
            
            # Filter for models that are either:
            # 1. Base GPT-4 models
            # 2. Previously fine-tuned models with our suffix
            available_models = []
            for model in models:
                model_id = model.id
                # Include GPT-4 base models
                if model_id.startswith(base_name):
                    available_models.append(model_id)
                # Include our fine-tuned models - check if suffix is anywhere in the model ID
                elif suffix.lower() in model_id.lower() and not model_id.rpartition('step-')[2].isdigit():
                    available_models.append(model_id)
                    self.logger.info(f"Found fine-tuned model: {model_id}")
            
            # Sort models: Base models first, then fine-tuned models
            def sort_key(model_name: str) -> tuple:
                """Sort key function to order models"""
                is_base = 1 if model_name.startswith(base_name) else 2
                return (is_base, model_name)
            
            sorted_models = sorted(available_models, key=sort_key)
            
            if not sorted_models:
                self.logger.warning("No base or fine-tuned models found")
                # Fallback to default model from config
                return [base_name]
            
            self.logger.info(f"Available models: {sorted_models}")
            return sorted_models
            
        except Exception as e:
            self.logger.error(f"Error fetching available models: {str(e)}")
            return [base_name]  # Fallback to default model