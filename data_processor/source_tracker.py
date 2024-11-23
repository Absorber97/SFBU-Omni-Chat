import json
import os
from typing import List, Dict
from datetime import datetime

class SourceTracker:
    def __init__(self, tracking_file: str = "fine_tuned_sources.json"):
        self.tracking_file = tracking_file
        self._ensure_tracking_file()
    
    def _ensure_tracking_file(self):
        """Ensure tracking file exists"""
        if not os.path.exists(self.tracking_file):
            with open(self.tracking_file, 'w') as f:
                json.dump([], f)
    
    def add_fine_tuned_source(self, source_info: Dict[str, str]):
        """Add a new fine-tuned source"""
        try:
            sources = self.get_fine_tuned_sources()
            source_info['timestamp'] = datetime.now().isoformat()
            sources.append(source_info)
            
            with open(self.tracking_file, 'w') as f:
                json.dump(sources, f, indent=2)
        except Exception as e:
            raise Exception(f"Error adding fine-tuned source: {str(e)}")
    
    def get_fine_tuned_sources(self) -> List[Dict[str, str]]:
        """Get list of fine-tuned sources"""
        try:
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Error reading fine-tuned sources: {str(e)}")
    
    def get_processed_sources(self) -> List[Dict[str, str]]:
        """Get list of processed sources from training data"""
        processed_sources = []
        try:
            if os.path.exists("training_data"):
                for timestamp_dir in os.listdir("training_data"):
                    dir_path = os.path.join("training_data", timestamp_dir)
                    if os.path.isdir(dir_path):
                        metadata_files = [f for f in os.listdir(dir_path) if f.endswith('_metadata.json')]
                        for metadata_file in metadata_files:
                            with open(os.path.join(dir_path, metadata_file), 'r') as f:
                                metadata = json.load(f)
                                processed_sources.extend([
                                    {
                                        'source': source,
                                        'timestamp': metadata['timestamp'],
                                        'dataset_name': metadata_file.replace('_metadata.json', '')
                                    }
                                    for source in metadata['sources']
                                ])
            return processed_sources
        except Exception as e:
            raise Exception(f"Error reading processed sources: {str(e)}") 