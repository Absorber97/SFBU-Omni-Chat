import gradio as gr
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from config import MODEL_CONFIG, get_fine_tuned_model_name
from datetime import datetime

def create_fine_tuning_tab(model_handler: Any) -> gr.Tab:
    """Create the fine-tuning tab interface"""
    
    def format_friendly_timestamp(timestamp: str) -> str:
        """Convert timestamp to user-friendly format"""
        try:
            # Convert YYYYMMDD_HHMMSS to datetime
            dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            return dt.strftime("%B %d, %Y %I:%M %p")
        except:
            return timestamp

    def get_dataset_type(name: str) -> str:
        """Determine dataset type from name"""
        if name.startswith('url_'):
            return '🌐 Web'
        elif name.startswith('pdf_'):
            return '📄 PDF'
        return '❓ Unknown'

    def get_dataset_status(dataset: Dict[str, Any]) -> str:
        """Get user-friendly status for dataset"""
        if dataset.get('fine_tuned'):
            status = dataset.get('fine_tuning_status', '').lower()
            if status == 'succeeded':
                return '✅ Fine-tuning Complete'
            elif status == 'failed':
                return '❌ Fine-tuning Failed'
            elif status == 'started':
                return '🔄 Fine-tuning in Progress'
            else:
                return '❓ Unknown Status'
        return '🟢 Available for Fine-tuning'

    def format_dataset_info(datasets: List[Dict[str, Any]]) -> pd.DataFrame:
        """Format dataset information for display"""
        if not datasets:
            return pd.DataFrame(columns=[
                'Type', 'Dataset', 'Sources', 'Examples', 
                'Split', 'Created', 'Status'
            ])
        
        formatted_data = []
        for dataset in datasets:
            # Load metadata from json file
            metadata = model_handler.load_dataset_metadata(dataset['path'])
            if not metadata:
                continue

            # Calculate split percentage
            total = metadata.get('total_examples', 0)
            train = metadata.get('train_examples', 0)
            val = metadata.get('val_examples', 0)
            split_str = f"{train}/{val}" if total > 0 else "0/0"

            formatted_data.append({
                'Type': get_dataset_type(dataset.get('name', '')),
                'Dataset': dataset.get('name', ''),
                'Sources': ', '.join(metadata.get('sources', {}).get('friendly', [])),
                'Examples': str(metadata.get('total_examples', 0)),
                'Split': split_str,
                'Created': format_friendly_timestamp(metadata.get('timestamp', '')),
                'Status': get_dataset_status(dataset)
            })
        
        df = pd.DataFrame(formatted_data)
        
        # Ensure all required columns exist and order
        column_order = ['Type', 'Dataset', 'Sources', 'Examples', 'Split', 'Created', 'Status']
        for col in column_order:
            if col not in df.columns:
                df[col] = ''
                
        return df[column_order]
    
    def get_available_base_models() -> List[str]:
        """Get list of available base models for fine-tuning"""
        return model_handler.get_available_base_models()
    
    def refresh_datasets() -> Tuple[pd.DataFrame, List[Tuple[str, str]], List[str]]:
        """Refresh the datasets list and dropdown options"""
        datasets = model_handler.source_tracker.get_training_datasets()
        base_models = get_available_base_models()  # Get actual available models
        
        if not base_models:
            base_models = ["No models available for fine-tuning"]
        
        available_datasets = [
            (d['name'], d['path']) 
            for d in datasets 
            if not d['fine_tuned']
        ]
        
        return (
            format_dataset_info(datasets),
            available_datasets,
            base_models
        )
    
    def start_fine_tuning(dataset_path: str, base_model: str) -> Dict[str, Any]:
        """Start fine-tuning with selected dataset and base model"""
        if not dataset_path:
            return {"error": "Please select a dataset"}
        if not base_model:
            return {"error": "Please select a base model"}
            
        return model_handler.start_fine_tuning(dataset_path, base_model)
    
    # Get initial data
    initial_table_data, initial_dataset_choices, initial_model_choices = refresh_datasets()
    
    with gr.Tab("🔧 Fine-tuning") as tab:
        # Available Datasets Section
        gr.Markdown("### 📚 Available Datasets")
        datasets_table = gr.DataFrame(
            value=initial_table_data,
            headers=['Type', 'Dataset', 'Sources', 'Examples', 'Split', 'Created', 'Status'],
            label="Available Datasets",
            interactive=False,
            wrap=True,
            height=300
        )
        
        # Model Selection Section
        gr.Markdown("### 🤖 Model Selection")
        with gr.Group():
            with gr.Row():
                dataset_dropdown = gr.Dropdown(
                    label="Select Dataset for Fine-tuning",
                    choices=initial_dataset_choices,
                    interactive=True,
                    info="Choose a dataset to fine-tune the model",
                    allow_custom_value=False
                )
                base_model_dropdown = gr.Dropdown(
                    label="Select Base Model",
                    choices=initial_model_choices,
                    value=initial_model_choices[0] if initial_model_choices else None,
                    interactive=True,
                    info="Choose an OpenAI model available for fine-tuning",
                    allow_custom_value=False
                )
            
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh Datasets", size="sm")
                fine_tune_btn = gr.Button(
                    "🚀 Start Fine-tuning", 
                    variant="primary",
                    size="sm"
                )
        
        # Training Status Section
        gr.Markdown("### 📊 Training Status")
        with gr.Group():
            training_status = gr.JSON(
                label="Current Training Status",
                visible=True
            )
            
            with gr.Row():
                job_id_input = gr.Textbox(
                    label="Job ID",
                    placeholder="Enter job ID to check status",
                    interactive=True,
                    info="Enter the job ID from a previous fine-tuning run"
                )
                check_status_btn = gr.Button(
                    "📊 Check Status",
                    size="sm"
                )

        # Event handlers
        refresh_btn.click(
            fn=refresh_datasets,
            outputs=[
                datasets_table,
                dataset_dropdown,
                base_model_dropdown
            ]
        )
        
        fine_tune_btn.click(
            fn=start_fine_tuning,
            inputs=[dataset_dropdown, base_model_dropdown],
            outputs=[training_status]
        )
        
        check_status_btn.click(
            fn=model_handler.check_fine_tuning_status,
            inputs=[job_id_input],
            outputs=[training_status]
        )
        
    return tab