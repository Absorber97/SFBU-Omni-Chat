from typing import Dict, List, Tuple
from datetime import datetime
from urllib.parse import urlparse

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
            if "messages" in item:
                messages = item["messages"]
                # Extract user question and assistant response
                user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
                assistant_msg = next((m["content"] for m in messages if m["role"] == "assistant"), "")
                
                formatted_data.append([
                    user_msg,  # Question/Prompt
                    assistant_msg,  # Answer/Completion
                    item.get('source', ''),
                    item.get('section', ''),
                    item.get('page', '')
                ])
            else:
                # Handle old format
                formatted_data.append([
                    item.get('prompt', ''),
                    item.get('completion', ''),
                    item.get('source', ''),
                    item.get('section', ''),
                    item.get('page', '')
                ])
        return formatted_data

    def process_url(
        self, 
        urls: str, 
        enable_recursion: bool = False, 
        enable_batch: bool = False,
        max_urls: int = 2
    ) -> Tuple[Dict, List[List[str]], List[List[str]]]:
        """Process URL(s) and return formatted data"""
        try:
            # Parse URLs based on batch mode
            url_list = self._parse_urls(urls, enable_batch)
            if not url_list:
                return (
                    {"status": "error", "message": "No valid URLs provided"},
                    [],
                    []
                )

            # Process each URL and collect results
            all_extracted_data = []
            for url in url_list:
                self.app.logger.info(f"Processing URL: {url}")
                extracted_data = self.app.url_extractor.extract_text(
                    url, 
                    enable_recursion, 
                    max_urls
                )
                if extracted_data:
                    all_extracted_data.extend(extracted_data)

            if not all_extracted_data:
                return (
                    {"status": "error", "message": "No data could be extracted from the URL(s)"},
                    [],
                    []
                )

            # Format all collected data
            formatted_data, source_metadata = self.app.jsonl_formatter.format_data(all_extracted_data)
            
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
                    'message': f"Processed {len(url_list)} URL(s), generated {len(formatted_data)} entries",
                    'files': files
                },
                train_preview,
                val_preview
            )
        except Exception as e:
            self.app.logger.error(f"Error processing URLs: {str(e)}")
            return (
                {"status": "error", "message": f"Error processing URLs: {str(e)}"},
                [],
                []
            )

    def _parse_urls(self, urls: str, enable_batch: bool) -> List[str]:
        """Parse and validate URLs from input"""
        if not urls.strip():
            return []
        
        # Split URLs if batch mode is enabled
        url_list = urls.strip().split('\n') if enable_batch else [urls.strip()]
        
        # Clean and validate URLs
        valid_urls = []
        for url in url_list:
            url = url.strip()
            if url and self._is_valid_url(url):
                valid_urls.append(url)
            else:
                self.app.logger.warning(f"Invalid URL skipped: {url}")
        
        return valid_urls

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False