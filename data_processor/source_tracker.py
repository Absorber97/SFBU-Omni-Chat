import json
import os
from typing import List, Dict
from datetime import datetime
from urllib.parse import urlparse

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
    
    def add_fine_tuned_source(self, source_info: Dict[str, str]):
        """Add a new fine-tuned source"""
        try:
            sources = self.get_fine_tuned_sources()  # Get existing or empty list
            source_info['timestamp'] = datetime.now().isoformat()
            # Format the file path if it exists
            if 'file_path' in source_info:
                source_info['display_name'] = self.format_source_path(source_info['file_path'])
            sources.append(source_info)
            
            # Only create/write file when actually adding a source
            with open(self.tracking_file, 'w') as f:
                json.dump(sources, f, indent=2)
        except Exception as e:
            raise Exception(f"Error adding fine-tuned source: {str(e)}")
    
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