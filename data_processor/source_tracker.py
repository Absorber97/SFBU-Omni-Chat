import json
import os
from typing import List, Dict, Any
from datetime import datetime
from urllib.parse import urlparse
import logging

class SourceTracker:
    def __init__(self, tracking_file: str = "fine_tuned_sources.json"):
        self.tracking_file = tracking_file
    
    def get_fine_tuned_sources(self) -> List[Dict[str, str]]:
        """Get list of fine-tuned sources"""
        try:
            if os.path.exists(self.tracking_file):
                with open(self.tracking_file, 'r') as f:
                    sources = json.load(f)
                    # Format display names for all sources
                    for source in sources:
                        if 'file_path' in source and 'display_name' not in source:
                            source['display_name'] = self.format_source_path(source['file_path'])
                    return sources
            return []  # Return empty list if file doesn't exist
        except Exception as e:
            return []  # Return empty list on error
    
    def add_fine_tuned_source(self, source_info: Dict[str, Any]):
        """Add or update fine-tuning information"""
        dataset_path = source_info['file_path']
        
        # Update source info
        if dataset_path in self.sources:
            self.sources[dataset_path].update({
                'fine_tuned': True,
                'fine_tuning_status': source_info.get('status', 'unknown'),
                'job_id': source_info.get('job_id'),
                'base_model': source_info.get('base_model'),
                'fine_tuning_timestamp': source_info.get('timestamp')
            })
        
        self._save_sources()
    
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
        except Exception:
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
                                if isinstance(metadata['sources'].get('friendly', []), list):
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
            raise Exception(f"Error reading processed sources: {str(e)}") 
    
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
            logging.error(f"Error getting training datasets: {str(e)}")
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