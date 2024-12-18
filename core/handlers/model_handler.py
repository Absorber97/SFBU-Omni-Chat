from typing import Dict, List, Any
from openai import OpenAI
from data_processor.source_tracker import SourceTracker
from config import OPENAI_API_KEY, MODEL_CONFIG, OPENAI_MODELS
from chat_interface.chat_manager import ChatManager
from datetime import datetime
import os
import json

class ModelHandler:
    def __init__(self, app):
        self.app = app
        self.source_tracker = SourceTracker()
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def start_fine_tuning(self, file_path: str, base_model: str) -> Dict:
        """Start fine-tuning process"""
        if not base_model:
            base_model = MODEL_CONFIG['base_name']
        
        try:
            if not file_path:
                return {
                    'status': 'error',
                    'message': 'No dataset selected'
                }
                
            self.app.logger.info(f"Starting fine-tuning with file: {file_path}")
            result = self.app.trainer.start_fine_tuning(file_path, base_model)
            
            if result['status'] == 'error':
                self.app.logger.error(f"Fine-tuning error: {result['error']}")
                return {
                    'status': 'error',
                    'message': str(result['error'])
                }
            
            # Update source tracker with fine-tuning status
            self.source_tracker.add_fine_tuned_source({
                'file_path': file_path,
                'job_id': result['job_id'],
                'status': 'started',
                'base_model': base_model,
                'timestamp': datetime.now().isoformat()
            })
            
            self.app.logger.info(f"Fine-tuning started successfully. Job ID: {result['job_id']}")
            return {
                'status': 'success',
                'message': f"Fine-tuning started. Job ID: {result['job_id']}",
                'job_id': result['job_id']
            }
            
        except Exception as e:
            self.app.logger.error(f"Error in fine-tuning: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def check_fine_tuning_status(self, job_id) -> Dict:
        """Check fine-tuning status"""
        try:
            self.app.logger.info(f"Checking status for job: {job_id}")
            status = self.app.trainer.check_status(job_id)
            
            if status['status'] == 'error':
                self.app.logger.error(f"Status check error: {status['error']}")
                return {
                    'status': 'error',
                    'message': str(status['error'])
                }
            
            self.app.logger.info(f"Status for job {job_id}: {status['status']}")
            return {
                'status': 'success',
                'job_status': status['status'],
                'model_id': status.get('fine_tuned_model'),
                'finished_at': status.get('finished_at')
            }
            
        except Exception as e:
            self.app.logger.error(f"Error checking status: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def get_chat_models(self) -> List[str]:
        """Get available models for chat interface"""
        try:
            self.app.logger.info("Fetching available models for chat")
            models = self.client.models.list()
            
            # Get our fine-tuning suffix from config
            suffix = MODEL_CONFIG['fine_tuned_suffix']
            
            # Filter and collect models with creation dates
            available_models = []
            for model in models:
                model_id = model.id
                # Include our fine-tuned models
                if (suffix.lower() in model_id.lower() and 
                    not model_id.rpartition('step-')[2].isdigit()):
                    available_models.append({
                        'id': model_id,
                        'created': getattr(model, 'created', 0)  # Fallback to 0 if created not available
                    })
            
            # Sort by creation date (descending) and extract just the model IDs
            sorted_models = sorted(
                available_models,
                key=lambda x: x['created'],
                reverse=True
            )
            
            return [model['id'] for model in sorted_models]
            
        except Exception as e:
            self.app.logger.error(f"Error fetching chat models: {str(e)}")
            return []

    def load_available_models(self) -> List[str]:
        """Load available models for chat interface"""
        try:
            return self.get_chat_models()
        except Exception as e:
            self.app.logger.error(f"Error loading available models: {str(e)}")
            return ["No models available"]

    def select_model(self, model_id: str) -> Dict:
        """Initialize chat manager with selected model"""
        try:
            self.app.logger.info(f"Selecting model: {model_id}")
            self.app.chat_manager.set_model(model_id)
            return {
                'status': 'success',
                'message': f"Model {model_id} selected successfully"
            }
        except Exception as e:
            self.app.logger.error(f"Error selecting model: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def get_available_base_models(self) -> List[str]:
        """Get list of available base models for fine-tuning"""
        try:
            self.app.logger.info("Fetching available models for fine-tuning")
            return self.app.trainer.get_available_models()
        except Exception as e:
            self.app.logger.error(f"Error fetching models: {str(e)}")
            return []

    def load_dataset_metadata(self, dataset_path: str) -> Dict[str, Any]:
        """Load metadata for a dataset"""
        try:
            # Convert dataset path to metadata path
            # e.g., training_data/20241123_184906/pdf_20241123_184906_train.jsonl 
            # -> training_data/20241123_184906/pdf_20241123_184906_metadata.json
            dir_path = os.path.dirname(dataset_path)
            file_name = os.path.basename(dataset_path).replace('_train.jsonl', '_metadata.json')
            metadata_path = os.path.join(dir_path, file_name)
            
            if not os.path.exists(metadata_path):
                self.app.logger.warning(f"Metadata file not found: {metadata_path}")
                return {}
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                return metadata
            
        except Exception as e:
            self.app.logger.error(f"Error loading dataset metadata: {str(e)}")
            return {}
 