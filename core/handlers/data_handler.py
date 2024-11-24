from typing import Dict, List, Tuple
from datetime import datetime

class DataHandler:
    def __init__(self, app):
        self.app = app
    
    def process_pdf(self, pdf_path) -> Tuple[Dict, List[List[str]], List[List[str]]]:
        """Process PDF with logging"""
        try:
            self.app.logger.info(f"Starting PDF processing: {pdf_path}")
            extracted_data = self.app.pdf_extractor.extract_text(pdf_path)
            self.app.logger.info(f"Extracted {len(extracted_data)} chunks from PDF")
            
            formatted_data, source_metadata = self.app.jsonl_formatter.format_data(extracted_data)
            dataset_name = f"pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            files = self.app.jsonl_formatter.save_jsonl(formatted_data, dataset_name, source_metadata)
            if not files:
                return (
                    {"status": "error", "message": "No data to process"},
                    [],
                    []
                )
            
            preview_data = self.app._load_preview_data(files['train_file'], files['val_file'])
            
            # Format preview data for Gradio Dataframe
            train_preview = self._format_preview_data(preview_data['train_preview'])
            val_preview = self._format_preview_data(preview_data['val_preview'])
            
            return (
                {
                    'status': 'success',
                    'message': f"Processed {len(formatted_data)} entries",
                    'files': files
                },
                train_preview,
                val_preview
            )
            
        except Exception as e:
            self.app.logger.error(f"Error processing PDF: {str(e)}")
            return (
                {'status': 'error', 'message': str(e)},
                [],
                []
            )

    def _format_preview_data(self, data: List[Dict]) -> List[List[str]]:
        """Format data for Gradio Dataframe display"""
        formatted_data = []
        for item in data:
            # Convert each dictionary item to a list format
            formatted_data.append([
                item.get('prompt', ''),  # Question
                item.get('completion', '')  # Answer
            ])
        return formatted_data

    def process_url(self, url: str, enable_recursion: bool = False, max_urls: int = 2) -> Tuple[Dict, List[List[str]], List[List[str]]]:
        """Process URL and return formatted data"""
        try:
            # Extract text from URL
            self.app.logger.info(f"Starting URL processing: {url} (recursion: {'enabled' if enable_recursion else 'disabled'})")
            extracted_data = self.app.url_extractor.extract_text(url, enable_recursion, max_urls)
            
            # Format data using JSONLFormatter
            formatted_data, source_metadata = self.app.jsonl_formatter.format_data(extracted_data)
            
            # Save the formatted data
            dataset_name = f"url_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            files = self.app.jsonl_formatter.save_jsonl(formatted_data, dataset_name, source_metadata)
            
            if not files:
                return (
                    {"status": "error", "message": "No data to process"},
                    [],
                    []
                )
            
            # Load preview data
            preview_data = self.app._load_preview_data(files['train_file'], files['val_file'])
            
            # Format preview data for Gradio Dataframe
            train_preview = self._format_preview_data(preview_data['train_preview'])
            val_preview = self._format_preview_data(preview_data['val_preview'])
            
            return (
                {
                    'status': 'success',
                    'message': f"Processed {len(formatted_data)} entries",
                    'files': files
                },
                train_preview,
                val_preview
            )
            
        except Exception as e:
            self.app.logger.error(f"Error processing URL: {str(e)}")
            return (
                {'status': 'error', 'message': str(e)},
                [],
                []
            )