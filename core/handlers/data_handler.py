from typing import Dict, List, Tuple
from datetime import datetime

class DataHandler:
    def __init__(self, app):
        self.app = app
    
    def process_pdf(self, pdf_path) -> Tuple[Dict, List, List]:
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
            
            return (
                {
                    'status': 'success',
                    'message': f"Processed {len(formatted_data)} entries",
                    'output_dir': self.app.jsonl_formatter.current_output_dir,
                    'train_file': files['train_file'],
                    'val_file': files['val_file'],
                    'metadata_file': files['metadata_file']
                },
                preview_data['train_preview'],
                preview_data['val_preview']
            )
            
        except Exception as e:
            self.app.logger.error(f"Error processing PDF: {str(e)}")
            return (
                {'status': 'error', 'message': str(e)},
                [],
                []
            )

    def process_url(self, url) -> Tuple[Dict, List, List]:
        """Process URL with logging"""
        try:
            self.app.logger.info(f"Starting URL processing: {url}")
            extracted_data = self.app.url_extractor.extract_text(url)
            self.app.logger.info(f"Extracted {len(extracted_data)} sections from URL")
            
            formatted_data, source_metadata = self.app.jsonl_formatter.format_data(extracted_data)
            dataset_name = f"url_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            files = self.app.jsonl_formatter.save_jsonl(formatted_data, dataset_name, source_metadata)
            if not files:
                return (
                    {"status": "error", "message": "No data to process"},
                    [],
                    []
                )
            
            preview_data = self.app._load_preview_data(files['train_file'], files['val_file'])
            
            return (
                {
                    'status': 'success',
                    'message': f"Processed {len(formatted_data)} entries",
                    'output_dir': self.app.jsonl_formatter.current_output_dir,
                    'train_file': files['train_file'],
                    'val_file': files['val_file'],
                    'metadata_file': files['metadata_file']
                },
                preview_data['train_preview'],
                preview_data['val_preview']
            )
        except Exception as e:
            self.app.logger.error(f"Error processing URL: {str(e)}")
            return (
                {'status': 'error', 'message': str(e)},
                [],
                []
            )