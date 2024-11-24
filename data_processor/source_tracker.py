import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
import logging

class SourceTracker:
    def __init__(self, tracking_file: str = "fine_tuned_sources.json"):
        self.tracking_file = tracking_file
        self.logger = logging.getLogger(__name__)
        self.sources: Dict[str, Dict[str, Any]] = self._load_sources()
    
    def _load_sources(self) -> Dict[str, Dict[str, Any]]:
        """Load sources from tracking file"""
        try:
            if os.path.exists(self.tracking_file):
                with open(self.tracking_file, 'r') as f:
                    data = json.load(f)
                    # Convert list format to dictionary if needed
                    if isinstance(data, list):
                        # Convert old list format to new dict format
                        sources_dict = {}
                        for source in data:
                            if 'file_path' in source:
                                sources_dict[source['file_path']] = {
                                    'fine_tuned': True,
                                    'fine_tuning_status': source.get('status', 'unknown'),
                                    'job_id': source.get('job_id'),
                                    'base_model': source.get('base_model'),
                                    'fine_tuning_timestamp': source.get('timestamp')
                                }
                        return sources_dict
                    return data if isinstance(data, dict) else {}
            return {}
        except Exception as e:
            self.logger.error(f"Error loading sources: {str(e)}")
            return {}
    
    def _save_sources(self):
        """Save sources to tracking file"""
        try:
            with open(self.tracking_file, 'w') as f:
                json.dump(self.sources, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving sources: {str(e)}")
    
    def get_fine_tuned_sources(self) -> List[Dict[str, Any]]:
        """Get list of fine-tuned sources"""
        try:
            sources_list = []
            if not self.sources:
                return []
            
            for file_path, info in self.sources.items():
                source_info = {
                    'file_path': file_path,
                    'display_name': self.format_source_path(file_path),
                    'status': info.get('fine_tuning_status', 'unknown'),
                    'job_id': info.get('job_id'),
                    'base_model': info.get('base_model'),
                    'timestamp': info.get('fine_tuning_timestamp')
                }
                sources_list.append(source_info)
            return sources_list
        except Exception as e:
            self.logger.error(f"Error getting fine-tuned sources: {str(e)}")
            return []
    
    def add_fine_tuned_source(self, source_info: Dict[str, Any]):
        """Add or update fine-tuning information"""
        try:
            if not source_info.get('file_path'):
                self.logger.error("No file path provided in source info")
                return
            
            dataset_path = source_info['file_path']
            
            # Update source info
            self.sources[dataset_path] = {
                'fine_tuned': True,
                'fine_tuning_status': source_info.get('status', 'unknown'),
                'job_id': source_info.get('job_id'),
                'base_model': source_info.get('base_model'),
                'fine_tuning_timestamp': source_info.get('timestamp')
            }
            
            self._save_sources()
        except Exception as e:
            self.logger.error(f"Error adding fine-tuned source: {str(e)}")
    
    def format_source_path(self, source_path: str) -> str:
        """Format source path for display - extract only the filename with extension"""
        try:
            if source_path.startswith(('http://', 'https://')):
                # For URLs, use domain and path
                parsed = urlparse(source_path)
                return f"{parsed.netloc}{parsed.path}"
            else:
                # For files, use basename
                return os.path.basename(source_path)
        except Exception as e:
            self.logger.error(f"Error formatting source path: {str(e)}")
            return source_path
    
    def get_processed_sources(self) -> List[Dict[str, str]]:
        """Get list of processed sources with friendly names only"""
        processed_sources = []
        try:
            if os.path.exists("training_data"):
                for timestamp_dir in os.listdir("training_data"):
                    dir_path = os.path.join("training_data", timestamp_dir)
                    if os.path.isdir(dir_path) and any(os.listdir(dir_path)):
                        metadata_files = [f for f in os.listdir(dir_path) if f.endswith('_metadata.json')]
                        for metadata_file in metadata_files:
                            with open(os.path.join(dir_path, metadata_file), 'r') as f:
                                metadata = json.load(f)
                                # Extract friendly sources from nested structure if needed
                                friendly_sources = []
                                if isinstance(metadata.get('sources', {}).get('friendly', []), list):
                                    friendly_sources = [
                                        src for src in metadata['sources']['friendly'] 
                                        if isinstance(src, str)  # Only include string URLs
                                    ]
                                processed_sources.append({
                                    'source': friendly_sources,
                                    'timestamp': timestamp_dir,
                                    'dataset_name': metadata_file.replace('_metadata.json', '')
                                })
            return processed_sources
        except Exception as e:
            self.logger.error(f"Error reading processed sources: {str(e)}")
            return []
    
    def get_training_datasets(self) -> List[Dict[str, Any]]:
        """Get all available training datasets with their fine-tuning status"""
        datasets = []
        try:
            if os.path.exists("training_data"):
                for timestamp_dir in os.listdir("training_data"):
                    dir_path = os.path.join("training_data", timestamp_dir)
                    if os.path.isdir(dir_path):
                        # Look for training files and metadata
                        train_files = [f for f in os.listdir(dir_path) 
                                     if f.endswith('_train.jsonl')]
                        
                        for train_file in train_files:
                            dataset_name = train_file.replace('_train.jsonl', '')
                            metadata_file = f"{dataset_name}_metadata.json"
                            metadata_path = os.path.join(dir_path, metadata_file)
                            
                            if os.path.exists(metadata_path):
                                with open(metadata_path, 'r') as f:
                                    metadata = json.load(f)
                                
                                # Check if this dataset has been fine-tuned
                                fine_tuned_sources = self.get_fine_tuned_sources()
                                fine_tuning_status = next(
                                    (source for source in fine_tuned_sources 
                                     if source['file_path'] == os.path.join(dir_path, train_file)),
                                    None
                                )
                                
                                datasets.append({
                                    'name': dataset_name,
                                    'path': os.path.join(dir_path, train_file),
                                    'timestamp': timestamp_dir,
                                    'sources': metadata['sources'].get('friendly', []),
                                    'fine_tuned': bool(fine_tuning_status),
                                    'status': fine_tuning_status['status'] if fine_tuning_status else None,
                                    'job_id': fine_tuning_status['job_id'] if fine_tuning_status else None,
                                    'metadata': metadata  # Include full metadata
                                })
                                
            return sorted(datasets, key=lambda x: x['timestamp'], reverse=True)
        except Exception as e:
            self.logger.error(f"Error getting training datasets: {str(e)}")
            return []
    
    def get_dataset_metadata(self, dataset_path: str) -> Dict[str, Any]:
        """Get metadata for a specific dataset"""
        try:
            # Convert training file path to metadata file path
            metadata_path = dataset_path.replace('_train.jsonl', '_metadata.json')
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Error reading metadata: {str(e)}")
            return {}