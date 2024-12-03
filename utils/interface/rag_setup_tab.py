import gradio as gr
from typing import Any, Dict, List, Tuple
import pandas as pd
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def create_rag_setup_tab(rag_handler: Any, model_handler: Any) -> gr.Tab:
    """Create the RAG setup tab interface"""
    
    def get_jsonl_files() -> List[str]:
        """Get list of JSONL files from rag_processing/data directory"""
        data_dir = Path("rag_processing/data")
        if not data_dir.exists():
            return []
        return [str(f.relative_to(data_dir)) for f in data_dir.glob("**/*.jsonl")]
    
    def get_indices() -> List[Dict[str, Any]]:
        """Get available RAG indices"""
        return rag_handler.get_available_indices()
    
    def format_indices(indices: List[Dict[str, Any]]) -> pd.DataFrame:
        """Format indices for display"""
        if not indices:
            return pd.DataFrame(columns=['Name', 'Created', 'Documents'])
        return pd.DataFrame([
            {
                'Name': idx['name'],
                'Created': idx['created_at'],
                'Documents': idx['document_count']
            }
            for idx in indices
        ])
    
    async def test_retrieval(query: str, k: int) -> pd.DataFrame:
        """Test RAG retrieval with a query"""
        try:
            logger.info(f"Testing RAG retrieval for query: {query}")
            results = await rag_handler.get_relevant_context(query, k)
            
            # Format results for display
            formatted_results = []
            for r in results:
                formatted_results.append({
                    'Question': r['metadata']['question'],
                    'Answer': r['metadata']['answer'],
                    'Score': f"{r['score']:.4f}",
                    'Source': r['metadata']['source']
                })
                
            logger.info(f"Found {len(formatted_results)} results")
            return pd.DataFrame(formatted_results)
        except Exception as e:
            logger.error(f"Error in test retrieval: {str(e)}", exc_info=True)
            return pd.DataFrame({
                'Error': [str(e)]
            })
    
    def refresh_indices() -> Tuple[gr.Dropdown, pd.DataFrame]:
        """Refresh the indices list and display"""
        indices = get_indices()
        formatted_indices = format_indices(indices)
        index_choices = [idx['name'] for idx in indices]
        return (
            gr.Dropdown(choices=index_choices, value=index_choices[0] if index_choices else None),
            formatted_indices
        )
    
    async def process_file_for_rag(file_name: str, index_name: str) -> Tuple[Dict[str, Any], pd.DataFrame, gr.Dropdown]:
        """Process selected JSONL file for RAG setup"""
        try:
            logger.info(f"Processing file {file_name} for RAG index {index_name}")
            if not file_name:
                logger.warning("No file selected")
                return (
                    {"status": "error", "message": "Please select a JSONL file"},
                    pd.DataFrame(),
                    gr.Dropdown()
                )
            if not index_name:
                logger.warning("No index name provided")
                return (
                    {"status": "error", "message": "Please provide an index name"},
                    pd.DataFrame(),
                    gr.Dropdown()
                )
                
            file_path = os.path.join("rag_processing/data", file_name)
            await rag_handler.process_jsonl_file(file_path, index_name)
            logger.info(f"Successfully processed file {file_name}")
            
            # Refresh indices display and selector
            indices = get_indices()
            formatted_indices = format_indices(indices)
            index_choices = [idx['name'] for idx in indices]
            
            return (
                {
                    "status": "success",
                    "message": f"Successfully processed {file_name} for RAG"
                },
                formatted_indices,
                gr.Dropdown(choices=index_choices, value=index_name)  # Set current index as selected
            )
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}", exc_info=True)
            return (
                {
                    "status": "error",
                    "message": f"Error processing file: {str(e)}"
                },
                pd.DataFrame(),
                gr.Dropdown()
            )
    
    def delete_index(index_name: str) -> Tuple[Dict[str, Any], pd.DataFrame, gr.Dropdown]:
        """Delete selected index"""
        try:
            rag_handler.delete_index(index_name)
            
            # Refresh indices
            indices = get_indices()
            formatted_indices = format_indices(indices)
            index_choices = [idx['name'] for idx in indices]
            
            return (
                {
                    "status": "success",
                    "message": f"Successfully deleted index: {index_name}"
                },
                formatted_indices,
                gr.Dropdown(choices=index_choices, value=index_choices[0] if index_choices else None)
            )
        except Exception as e:
            return (
                {
                    "status": "error",
                    "message": f"Error deleting index: {str(e)}"
                },
                pd.DataFrame(columns=['Name', 'Created', 'Documents']),
                gr.Dropdown()
            )
    
    def load_index(index_name: str) -> Dict[str, Any]:
        """Load selected index"""
        try:
            rag_handler._load_index(index_name)
            return {
                "status": "success",
                "message": f"Successfully loaded index: {index_name}",
                "active_index": index_name
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error loading index: {str(e)}",
                "active_index": None
            }
    
    def refresh_file_list():
        """Refresh the list of available JSONL files"""
        files = get_jsonl_files()
        return gr.Dropdown(choices=files, value=files[0] if files else None)
    
    initial_files = get_jsonl_files()
    initial_indices = get_indices()
    
    with gr.Tab("🔍 RAG Setup") as tab:
        gr.Markdown("### 📚 RAG Configuration")
        
        with gr.Group():
            # File selection
            file_input = gr.Dropdown(
                label="Select Training Data",
                choices=initial_files,
                value=initial_files[0] if initial_files else None,
                info="Select a JSONL file from rag_processing/data directory"
            )
            
            # Index name input
            index_name_input = gr.Textbox(
                label="Index Name",
                placeholder="Enter a name for the new index",
                info="Provide a unique name for this RAG index"
            )
            
            with gr.Row():
                refresh_files_btn = gr.Button("🔄 Refresh Files", size="sm")
                process_btn = gr.Button("⚡ Process for RAG", variant="primary")
            
            status_output = gr.JSON(label="Processing Status")
        
        gr.Markdown("### 💾 Stored Indices")
        with gr.Group():
            indices_df = gr.DataFrame(
                value=format_indices(initial_indices),
                headers=['Name', 'Created', 'Documents'],
                label="Available Indices",
                interactive=False
            )
            
            with gr.Row():
                index_selector = gr.Dropdown(
                    label="Select Index",
                    choices=[idx['name'] for idx in initial_indices],
                    info="Select an index to load or delete"
                )
                load_btn = gr.Button("📥 Load Index", size="sm")
                delete_btn = gr.Button("🗑️ Delete Index", size="sm", variant="stop")
        
        gr.Markdown("### 🧪 Test Retrieval")
        with gr.Group():
            with gr.Row():
                test_query = gr.Textbox(
                    label="Test Query",
                    placeholder="Enter a test question"
                )
                top_k = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=3,
                    step=1,
                    label="Number of Results"
                )
            
            test_btn = gr.Button("🔍 Test Retrieval")
            
            results_df = gr.DataFrame(
                label="Retrieved Contexts",
                headers=['Question', 'Answer', 'Score', 'Source']
            )
        
        # Event handlers
        refresh_files_btn.click(
            fn=refresh_file_list,
            outputs=[file_input]
        )
        
        process_btn.click(
            fn=process_file_for_rag,
            inputs=[file_input, index_name_input],
            outputs=[status_output, indices_df, index_selector],
            api_name="process_rag_file"
        )
        
        load_btn.click(
            fn=load_index,
            inputs=[index_selector],
            outputs=[status_output]
        )
        
        delete_btn.click(
            fn=delete_index,
            inputs=[index_selector],
            outputs=[status_output, indices_df, index_selector]
        )
        
        test_btn.click(
            fn=test_retrieval,
            inputs=[test_query, top_k],
            outputs=[results_df],
            api_name="test_rag_retrieval"
        )
        
    return tab 