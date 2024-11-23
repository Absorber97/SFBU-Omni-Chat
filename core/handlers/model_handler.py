from typing import Dict, List
from data_processor.source_tracker import SourceTracker
from config import OPENAI_API_KEY

class ModelHandler:
    def __init__(self, app):
        self.app = app
        self.source_tracker = SourceTracker()
    
    def start_fine_tuning(self, file_path) -> Dict:
        """Start fine-tuning process"""
        try:
            self.app.logger.info(f"Starting fine-tuning with file: {file_path}")
            result = self.app.trainer.start_fine_tuning(file_path)
            
            if result['status'] == 'error':
                self.app.logger.error(f"Fine-tuning error: {result['error']}")
                return {
                    'status': 'error',
                    'message': str(result['error'])
                }
            
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

    def load_available_models(self) -> List[str]:
        """Get list of available fine-tuned models"""
        try:
            self.app.logger.info("Loading available fine-tuned models")
            sources = self.source_tracker.get_fine_tuned_sources()
            models = [s.get('fine_tuned_model') for s in sources 
                     if s.get('status') == 'succeeded' and s.get('fine_tuned_model')]
            return models
        except Exception as e:
            self.app.logger.error(f"Error loading models: {str(e)}")
            return []

    def select_model(self, model_id: str) -> Dict:
        """Initialize chat manager with selected model"""
        try:
            self.app.logger.info(f"Selecting model: {model_id}")
            self.app.chat_manager = ChatManager(api_key=OPENAI_API_KEY)
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