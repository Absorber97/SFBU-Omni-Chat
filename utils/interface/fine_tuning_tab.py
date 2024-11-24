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
            if status in ['succeeded', 'success']:
                return '✅ Fine-tuning Complete'
            elif status in ['failed', 'error', 'cancelled', 'stopping', 'failure']:
                return '❌ Fine-tuning Failed'
            elif status in ['started', 'running', 'validating_files', 'queued']:
                return f'🔄 {status}'
            else:
                return '❓ Unknown Status'
        return '🟢 Available for Fine-tuning'

    def format_dataset_info(datasets: List[Dict[str, Any]]) -> pd.DataFrame:
        """Format dataset information for display"""
        if not datasets:
            return pd.DataFrame(columns=[
                'Type', 'Dataset', 'Sources', 'Examples', 
                'Split', 'Created'
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
                'Created': format_friendly_timestamp(metadata.get('timestamp', ''))
            })
        
        df = pd.DataFrame(formatted_data)
        
        # Ensure all required columns exist and order
        column_order = ['Type', 'Dataset', 'Sources', 'Examples', 'Split', 'Created']
        for col in column_order:
            if col not in df.columns:
                df[col] = ''
                
        return df[column_order]
    
    def get_available_base_models() -> List[str]:
        """Get list of available base models for fine-tuning"""
        return model_handler.get_available_base_models()
    
    def refresh_datasets() -> Tuple[pd.DataFrame, Dict, Dict]:
        """Refresh the datasets list and dropdown options"""
        datasets = model_handler.source_tracker.get_training_datasets()
        base_models = model_handler.get_available_base_models()
        
        # Format dataset choices for dropdown - only show name, not full path
        available_datasets = [
            d['name'] for d in datasets 
            if not d.get('fine_tuned', False)
        ]
        
        if not available_datasets:
            available_datasets = ["No datasets available"]
        
        if not base_models:
            base_models = ["No models available"]
            
        return (
            format_dataset_info(datasets),
            {
                "choices": available_datasets,
                "value": available_datasets[0] if available_datasets else None
            },
            {
                "choices": base_models,
                "value": base_models[0] if base_models else None
            }
        )
    
    def start_fine_tuning(dataset_name: str, base_model: str) -> Dict:
        """Start fine-tuning process"""
        if not dataset_name or dataset_name == "No datasets available":
            return {'status': 'error', 'message': 'Please select a valid dataset'}
            
        if not base_model or base_model == "No models available":
            return {'status': 'error', 'message': 'Please select a valid base model'}
            
        # Find the full path for the selected dataset name
        datasets = model_handler.source_tracker.get_training_datasets()
        dataset = next((d for d in datasets if d['name'] == dataset_name), None)
        
        if not dataset:
            return {'status': 'error', 'message': 'Dataset not found'}
            
        return model_handler.start_fine_tuning(dataset['path'], base_model)
    
    # Initial data
    initial_datasets = model_handler.source_tracker.get_training_datasets()
    initial_table_data = format_dataset_info(initial_datasets)
    
    # Initial dropdown choices
    initial_dataset_choices = [
        d['name'] for d in initial_datasets         
    ] or ["No datasets available"]
    
    initial_model_choices = model_handler.get_available_base_models() or ["No models available"]

    with gr.Tab("🔧 Fine-tuning") as tab:
        # Available Datasets Section
        gr.Markdown("### 📚 Available Datasets")
        datasets_table = gr.DataFrame(
            value=initial_table_data,
            headers=['Type', 'Dataset', 'Sources', 'Examples', 'Split', 'Created'],
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
                    value=initial_dataset_choices[0] if initial_dataset_choices else None,
                    interactive=True,
                    info="Choose a dataset to fine-tune the model"
                )
                base_model_dropdown = gr.Dropdown(
                    label="Select Base Model",
                    choices=initial_model_choices,
                    value=initial_model_choices[0] if initial_model_choices else None,
                    interactive=True,
                    info="Choose an OpenAI model available for fine-tuning"
                )
            
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh", size="sm")
                fine_tune_btn = gr.Button(
                    "🚀 Start Fine-tuning", 
                    variant="primary",
                    size="sm"
                )
        
        # Training Status Section
        gr.Markdown("### 📊 Training Status")
        with gr.Group():
            with gr.Row():
                training_status = gr.JSON(
                    label="Current Training Status",
                    visible=True
                )
                openai_link = gr.HTML(
                    value='<div style="text-align: right; padding: 10px;">'
                          '<a href="https://platform.openai.com/finetune" '
                          'target="_blank" style="text-decoration: none; '
                          'padding: 8px 15px; border-radius: 5px; '
                          'background-color: #2D3748; color: white; '
                          'display: inline-flex; align-items: center; gap: 5px;">'
                          '🔗 Visit OpenAI Fine-tuning Dashboard</a></div>'
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