import gradio as gr
from typing import Dict, List, Any
import pandas as pd

def create_fine_tuning_tab(model_handler: Any) -> None:
    """Create the fine-tuning tab interface"""
    
    def format_dataset_info(datasets: List[Dict[str, Any]]) -> pd.DataFrame:
        """Format dataset information for display"""
        data = []
        for ds in datasets:
            status = "✅ Fine-tuned" if ds['fine_tuned'] else "⏳ Available"
            if ds['fine_tuned'] and ds['status']:
                status = f"✅ {ds['status'].title()}"
                
            data.append({
                'Dataset': ds['name'],
                'Timestamp': ds['timestamp'],
                'Sources': ', '.join(ds['sources']),
                'Status': status
            })
        return pd.DataFrame(data)
    
    def refresh_datasets():
        """Refresh the list of available datasets"""
        datasets = model_handler.source_tracker.get_training_datasets()
        return (
            format_dataset_info(datasets),
            gr.Dropdown(
                choices=[d['path'] for d in datasets if not d['fine_tuned']],
                label="Select Dataset for Fine-tuning",
                interactive=True
            )
        )
    
    def start_fine_tuning(dataset_path: str) -> Dict:
        """Start fine-tuning process"""
        if not dataset_path:
            return {
                "status": "error",
                "message": "Please select a dataset to fine-tune"
            }
        return model_handler.start_fine_tuning(dataset_path)
    
    with gr.Tab("🔧 Fine-tuning"):
        with gr.Row():
            with gr.Column():
                datasets_table = gr.DataFrame(
                    headers=['Dataset', 'Timestamp', 'Sources', 'Status'],
                    label="Available Datasets",
                    interactive=False
                )
                
                dataset_dropdown = gr.Dropdown(
                    label="Select Dataset for Fine-tuning",
                    interactive=True
                )
                
                refresh_btn = gr.Button("🔄 Refresh Datasets")
                
                fine_tune_btn = gr.Button("🚀 Start Fine-tuning", 
                                        variant="primary")
                
                job_id_input = gr.Textbox(
                    label="Job ID",
                    placeholder="Enter job ID to check status",
                    interactive=True
                )
                
                check_status_btn = gr.Button("📊 Check Status")
                
            with gr.Column():
                training_status = gr.JSON(
                    label="Training Status",
                    visible=True
                )
                
                current_status = gr.JSON(
                    label="Current Status",
                    visible=True
                )
                
                available_models = gr.Dropdown(
                    label="Available Models",
                    choices=[],
                    interactive=True
                )
                
                refresh_models_btn = gr.Button("🔄 Refresh Models")
        
        # Event handlers
        refresh_btn.click(
            refresh_datasets,
            outputs=[datasets_table, dataset_dropdown]
        )
        
        fine_tune_btn.click(
            start_fine_tuning,
            inputs=[dataset_dropdown],
            outputs=[training_status]
        )
        
        check_status_btn.click(
            model_handler.check_fine_tuning_status,
            inputs=[job_id_input],
            outputs=[current_status]
        )
        
        refresh_models_btn.click(
            model_handler.load_available_models,
            outputs=[available_models]
        )
        
        # Initial load
        refresh_datasets() 