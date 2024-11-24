import gradio as gr
import os
from typing import Any
from .interface.data_processing_tab import create_data_processing_tab
from .interface.fine_tuning_tab import create_fine_tuning_tab
from .interface.chat_tab import create_chat_tab

def create_interface(app: Any, data_handler: Any, model_handler: Any) -> gr.Blocks:
    """Create Gradio interface with all components"""
    
    def update_logs():
        """Get real-time logs"""
        return app.logger.get_logs()
    
    def get_source_info():
        """Get information about processed and fine-tuned sources"""
        try:
            tracker = model_handler.source_tracker
            return {
                'processed_sources': tracker.get_processed_sources(),
                'fine_tuned_sources': tracker.get_fine_tuned_sources()
            }
        except Exception as e:
            return {'error': str(e)}
    
    # Get absolute paths to images
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sfbu_logo_path = os.path.join(current_dir, "assets", "images", "SFBU.jpeg")
    
    # Convert image path to data URL
    def get_image_data_url(image_path):
        import base64
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/jpeg;base64,{encoded_string}"

    sfbu_logo_data_url = get_image_data_url(sfbu_logo_path)
    
    with gr.Blocks(title="SFBU Omni Chat") as interface:
        # Header with logo
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
                width: 64px !important;
                height: 64px !important;
                object-fit: contain !important;
            }}
            .header-title {{
                margin: 0 !important;
                padding: 0 !important;
            }}
            </style>
        """)

        # Create tabs
        create_data_processing_tab(data_handler, update_logs, get_source_info)
        create_fine_tuning_tab(model_handler)
        create_chat_tab(app, model_handler)

    return interface 