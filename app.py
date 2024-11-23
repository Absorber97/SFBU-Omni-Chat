import gradio as gr
import os
from data_processor.extractors.pdf_extractor import PDFExtractor
from data_processor.extractors.url_extractor import URLExtractor
from data_processor.formatters.jsonl_formatter import JSONLFormatter
from data_processor.fine_tuning.trainer import ModelTrainer
from chat_interface.chat_manager import ChatManager
from config import OPENAI_API_KEY
import logging
import sys
from datetime import datetime
import json
from data_processor.source_tracker import SourceTracker
import typing
from typing import Optional, Dict, List
from utils.logging_handler import RealTimeLogger

class SFBUApp:
    def __init__(self):
        self.logger = RealTimeLogger(__name__)
        self.pdf_extractor = PDFExtractor()
        self.url_extractor = URLExtractor()
        self.jsonl_formatter = JSONLFormatter(
            output_dir="training_data",
            api_key=os.getenv('OPENAI_API_KEY'),
            batch_size=5  # Process 5 items at a time
        )
        
        # Check if API key exists
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.trainer = ModelTrainer(api_key=OPENAI_API_KEY)
        self.chat_manager: Optional[ChatManager] = None
        
    def process_pdf(self, pdf_path):
        """Process PDF with logging"""
        try:
            self.logger.info(f"Starting PDF processing: {pdf_path}")
            extracted_data = self.pdf_extractor.extract_text(pdf_path)
            self.logger.info(f"Extracted {len(extracted_data)} chunks from PDF")
            
            formatted_data, source_metadata = self.jsonl_formatter.format_data(extracted_data)
            dataset_name = f"pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Save with train/val split
            files = self.jsonl_formatter.save_jsonl(formatted_data, dataset_name, source_metadata)
            if not files:  # Handle case when no data is saved
                return (
                    {"status": "error", "message": "No data to process"},
                    [],  # Empty train_preview
                    []   # Empty val_preview 
                )
            
            # Load preview data
            preview_data = self._load_preview_data(files['train_file'], files['val_file'])
            
            return (
                {
                    'status': 'success',
                    'message': f"Processed {len(formatted_data)} entries",
                    'output_dir': self.jsonl_formatter.current_output_dir,
                    'train_file': files['train_file'],
                    'val_file': files['val_file'],
                    'metadata_file': files['metadata_file']
                },
                preview_data['train_preview'],
                preview_data['val_preview']
            )
        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            return (
                {'status': 'error', 'message': str(e)},
                [],  # Empty train_preview
                []   # Empty val_preview
            )

    def _load_preview_data(self, train_file: str, val_file: str) -> Dict:
        """Load preview data from JSONL files"""
        preview_limit = 5  # Number of examples to show
        
        def load_jsonl_preview(file_path: str, limit: int) -> List[List]:
            data = []
            try:
                with open(file_path, 'r') as f:
                    for i, line in enumerate(f):
                        if i >= limit:
                            break
                        item = json.loads(line)
                        # Convert dict to list format for Dataframe
                        data.append([
                            item['prompt'],
                            item['completion']
                        ])
            except Exception as e:
                self.logger.error(f"Error loading preview data: {str(e)}")
            return data

        return {
            'train_preview': load_jsonl_preview(train_file, preview_limit),
            'val_preview': load_jsonl_preview(val_file, preview_limit)
        }

    def process_url(self, url):
        """Process URL with logging"""
        try:
            self.logger.info(f"Starting URL processing: {url}")
            extracted_data = self.url_extractor.extract_text(url)
            self.logger.info(f"Extracted {len(extracted_data)} sections from URL")
            
            formatted_data, source_metadata = self.jsonl_formatter.format_data(extracted_data)
            dataset_name = f"url_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Save with train/val split
            files = self.jsonl_formatter.save_jsonl(formatted_data, dataset_name, source_metadata)
            if not files:
                return {
                    "status": "error", 
                    "message": "No data to process"
                }
            
            # Load preview data
            preview_data = self._load_preview_data(files['train_file'], files['val_file'])
            
            return {
                'status': 'success',
                'message': f"Processed {len(formatted_data)} entries",
                'output_dir': self.jsonl_formatter.current_output_dir,
                'train_file': files['train_file'],
                'val_file': files['val_file'],
                'metadata_file': files['metadata_file']
            }
        except Exception as e:
            self.logger.error(f"Error processing URL: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def start_fine_tuning(self, file_path):
        """Start fine-tuning process"""
        try:
            self.logger.info(f"Starting fine-tuning with file: {file_path}")
            result = self.trainer.start_fine_tuning(file_path)
            
            if result['status'] == 'error':
                self.logger.error(f"Fine-tuning error: {result['error']}")
                return {
                    'status': 'error',
                    'message': str(result['error'])
                }
            
            self.logger.info(f"Fine-tuning started successfully. Job ID: {result['job_id']}")
            return {
                'status': 'success',
                'message': f"Fine-tuning started. Job ID: {result['job_id']}",
                'job_id': result['job_id']
            }
            
        except Exception as e:
            self.logger.error(f"Error in fine-tuning: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def check_fine_tuning_status(self, job_id):
        """Check fine-tuning status"""
        try:
            self.logger.info(f"Checking status for job: {job_id}")
            status = self.trainer.check_status(job_id)
            
            if status['status'] == 'error':
                self.logger.error(f"Status check error: {status['error']}")
                return {
                    'status': 'error',
                    'message': str(status['error'])
                }
            
            self.logger.info(f"Status for job {job_id}: {status['status']}")
            return {
                'status': 'success',
                'job_status': status['status'],
                'model_id': status.get('fine_tuned_model'),
                'finished_at': status.get('finished_at')
            }
            
        except Exception as e:
            self.logger.error(f"Error checking status: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def chat(self, message, history):
        """Handle chat interaction"""
        if not self.chat_manager:
            return "👋 Hi there! Please select a fine-tuned model first to start our conversation. 🤖"
        
        result = self.chat_manager.generate_response(message)
        if result['status'] == 'success':
            return result['response']
        return f"🤔 Oops! Something went wrong: {result['error']} Please try again!"

    def load_available_models(self):
        """Get list of available fine-tuned models"""
        try:
            self.logger.info("Loading available fine-tuned models")
            tracker = SourceTracker()
            sources = tracker.get_fine_tuned_sources()
            models = [s.get('fine_tuned_model') for s in sources 
                     if s.get('status') == 'succeeded' and s.get('fine_tuned_model')]
            return models
        except Exception as e:
            self.logger.error(f"Error loading models: {str(e)}")
            return []

    def select_model(self, model_id: str):
        """Initialize chat manager with selected model"""
        try:
            if model_id:
                self.logger.info(f"Initializing chat manager with model: {model_id}")
                self.chat_manager = ChatManager(model_id, OPENAI_API_KEY)
                return {"status": "Model loaded", "model_id": model_id}
            return {"status": "No model loaded"}
        except Exception as e:
            self.logger.error(f"Error selecting model: {str(e)}")
            return {"status": "error", "message": str(e)}

    def clear_chat(self):
        """Clear chat history"""
        if self.chat_manager:
            self.chat_manager.clear_history()
        return None

# Create Gradio interface
def create_interface():
    app = SFBUApp()
    
    def update_logs():
        """Get real-time logs"""
        return app.logger.get_logs()
    
    def get_source_info():
        """Get information about processed and fine-tuned sources"""
        try:
            tracker = SourceTracker()
            sources = tracker.get_processed_sources()
            
            # Format sources for display
            formatted_sources = []
            for source in sources:
                formatted_sources.append({
                    'Source': source['source'],
                    'Processed': source['timestamp'],
                    'Dataset': source['dataset_name']
                })
            
            return {
                'processed_sources': formatted_sources,
                'fine_tuned_sources': tracker.get_fine_tuned_sources()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def update_preview(output_dir: str):
        """Update preview with processed data"""
        if not output_dir or not os.path.exists(output_dir):
            return [], []
            
        train_file = [f for f in os.listdir(output_dir) if f.endswith('_train.jsonl')]
        val_file = [f for f in os.listdir(output_dir) if f.endswith('_val.jsonl')]
        
        train_data = []
        val_data = []
        
        if train_file:
            with open(os.path.join(output_dir, train_file[0]), 'r') as f:
                for line in f:
                    item = json.loads(line)
                    train_data.append([item['prompt'], item['completion']])
                    
        if val_file:
            with open(os.path.join(output_dir, val_file[0]), 'r') as f:
                for line in f:
                    item = json.loads(line)
                    val_data.append([item['prompt'], item['completion']])
                    
        return train_data[:5], val_data[:5]  # Show first 5 entries
    
    # Get absolute paths to images
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sfbu_logo_path = os.path.join(current_dir, "assets", "images", "SFBU.jpeg")
    bayhawk_path = os.path.join(current_dir, "assets", "images", "Bayhawk.jpeg")
    
    # Verify images exist
    if not os.path.exists(sfbu_logo_path):
        raise FileNotFoundError(f"SFBU logo not found at: {sfbu_logo_path}")
    if not os.path.exists(bayhawk_path):
        raise FileNotFoundError(f"Bayhawk image not found at: {bayhawk_path}")

    # Convert image path to data URL
    def get_image_data_url(image_path):
        import base64
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/jpeg;base64,{encoded_string}"

    sfbu_logo_data_url = get_image_data_url(sfbu_logo_path)
    
    with gr.Blocks(title="SFBU Omni Chat") as interface:
        # Header with logo and title using data URL
        gr.Markdown(f"""
            <div class="header-row">
                <div class="sfbu-logo-container">
                    <img src="{sfbu_logo_data_url}" class="sfbu-logo" alt="SFBU Logo">
                </div>
                <h1 class="header-title">Your SFBU Omni Assistant</h1>
            </div>
            <style>
            .header-row {{
                display: flex;
                align-items: center;
                gap: 20px;
                padding: 10px 20px;
                border-bottom: 2px solid #003366;
            }}
            .sfbu-logo {{
                flex: 0 0 64px;  /* Fixed size, won't grow or shrink */
                width: 64px !important;
                height: 64px !important;
                object-fit: contain !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            .header-title {{
                flex: 1;
                margin: 0 !important;
                padding: 0 !important;
            }}
            .header-title h1 {{
                margin: 0 !important;
                line-height: 64px !important;
            }}
            </style>
        """)

        with gr.Tab("🔄 Data Processing"):
            with gr.Row():
                with gr.Column():
                    pdf_input = gr.File(label="📄 Upload PDF")
                    process_pdf_btn = gr.Button("📥 Process PDF")
                    url_input = gr.Textbox(label="🔗 Enter URL")
                    process_url_btn = gr.Button("🌐 Process URL")
            
            # Status, logging, and source tracking display
            with gr.Row():
                with gr.Column():
                    process_output = gr.JSON(label="📊 Processing Result")
                    log_output = gr.Textbox(label="📝 Processing Logs", lines=10)
                with gr.Column():
                    sources_display = gr.JSON(
                        label="📚 Data Sources",
                        value=get_source_info()
                    )
                    refresh_sources = gr.Button("🔄 Refresh Sources")
            
            with gr.Row():
                with gr.Column():
                    train_preview = gr.Dataframe(
                        headers=["prompt", "completion"],
                        label="🎯 Training Data Preview"
                    )
                    val_preview = gr.Dataframe(
                        headers=["prompt", "completion"],
                        label="✅ Validation Data Preview"
                    )

        with gr.Tab("🔧 Fine-tuning"):
            with gr.Row():
                with gr.Column():
                    training_file = gr.File(label="📄 Select Training File (JSONL)")
                    start_ft_btn = gr.Button("🚀 Start Fine-tuning")
                with gr.Column():
                    job_id_input = gr.Textbox(label="🔍 Job ID")
                    check_status_btn = gr.Button("📊 Check Status")
            
            with gr.Row():
                ft_status_output = gr.JSON(label="📈 Fine-tuning Status")
                ft_log_output = gr.Textbox(label="📝 Fine-tuning Logs", lines=10)

        with gr.Tab("💬 Chat"):
            with gr.Row():
                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(
                        height=600,
                        label="🤖 SFBU Omni Chat",
                        avatar_images=(bayhawk_path, None),  # Use absolute path
                        show_copy_button=True,
                        elem_classes="chat-window"
                    )
                    msg = gr.Textbox(
                        label="✍️ Type your message",
                        placeholder="Ask me anything about SFBU...",
                        lines=2
                    )
                    with gr.Row():
                        submit_btn = gr.Button("📤 Send")
                        clear_btn = gr.Button("🗑️ Clear Chat")
                
                with gr.Column(scale=1):
                    model_info = gr.JSON(
                        label="🤖 Active Model Info",
                        value={"status": "No model loaded"}
                    )
                    available_models = gr.Dropdown(
                        label="📚 Available Fine-tuned Models",
                        choices=[],
                        interactive=True
                    )
                    refresh_models_btn = gr.Button("🔄 Refresh Models")

        # Update CSS styling
        gr.Markdown("""
        <style>
        .header-row {
            display: flex;
            align-items: center;
            gap: 20px;
            padding: 10px 20px;
            background: #f7f7f7;
            border-bottom: 2px solid #003366;
        }
        .sfbu-logo {
            flex: 0 0 64px;  /* Fixed size, won't grow or shrink */
            width: 64px !important;
            height: 64px !important;
            object-fit: contain !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .header-title {
            flex: 1;
            margin: 0 !important;
            padding: 0 !important;
        }
        .header-title h1 {
            margin: 0 !important;
            line-height: 64px !important;
        }
        .chat-window {
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
        """)

        # Add footer with SFBU branding
        gr.Markdown("""
        ### 🎓 SFBU Omni Chat
        Your intelligent assistant for all things SFBU! 
        
        Features:
        - 📚 Process university documents and websites
        - 🤖 Fine-tune AI models with SFBU-specific knowledge
        - 💬 Get instant answers about programs, admissions, and more!
        
        Powered by San Francisco Bay University . Guided By Prof. Henry Chang
        """)

        # Event handlers
        refresh_sources.click(
            fn=get_source_info,
            outputs=[sources_display]
        )

        process_pdf_btn.click(
            fn=app.process_pdf,
            inputs=[pdf_input],
            outputs=[process_output, train_preview, val_preview]
        ).then(
            fn=update_logs,
            outputs=[log_output]
        ).then(
            fn=get_source_info,
            outputs=[sources_display]
        )

        process_url_btn.click(
            fn=app.process_url,
            inputs=[url_input],
            outputs=[process_output]
        ).then(
            fn=lambda x: update_preview(x.get('output_dir')) if isinstance(x, dict) else ([], []),
            inputs=[process_output],
            outputs=[train_preview, val_preview]
        ).then(
            fn=update_logs,
            outputs=[log_output]
        ).then(
            fn=get_source_info,
            outputs=[sources_display]
        )

        # Event handlers for fine-tuning
        start_ft_btn.click(
            fn=app.start_fine_tuning,
            inputs=[training_file],
            outputs=[ft_status_output]
        ).then(
            fn=update_logs,
            outputs=[ft_log_output]
        )
        
        check_status_btn.click(
            fn=app.check_fine_tuning_status,
            inputs=[job_id_input],
            outputs=[ft_status_output]
        )

        # Chat event handlers
        msg.submit(
            fn=app.chat,
            inputs=[msg, chatbot],
            outputs=[chatbot]
        ).then(
            fn=lambda: "",
            outputs=[msg]
        )
        
        submit_btn.click(
            fn=app.chat,
            inputs=[msg, chatbot],
            outputs=[chatbot]
        ).then(
            fn=lambda: "",
            outputs=[msg]
        )
        
        clear_btn.click(
            fn=app.clear_chat,
            outputs=[chatbot]
        )
        
        refresh_models_btn.click(
            fn=app.load_available_models,
            outputs=available_models
        )
        
        available_models.change(
            fn=app.select_model,
            inputs=[available_models],
            outputs=[model_info]
        )

    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch() 