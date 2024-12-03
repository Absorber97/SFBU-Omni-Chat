import gradio as gr
from typing import Tuple, Callable, Dict, Any
from config import OPENAI_MODELS, ModelType
import logging

logger = logging.getLogger(__name__)

class ModelRAGSelector:
    def __init__(self, model_handler, rag_handler):
        self.model_handler = model_handler
        self.rag_handler = rag_handler
        logger.info("Initialized ModelRAGSelector")
        
    def get_available_models(self):
        """Get list of available models"""
        try:
            logger.info("Getting available models")
            models = self.model_handler.get_available_models()
            if models:
                logger.info(f"Found {len(models)} models")
                return models
            logger.warning("No models found, using defaults")
            return OPENAI_MODELS.get(ModelType.CHAT.value, [])
        except Exception as e:
            logger.error(f"Error getting models: {str(e)}", exc_info=True)
            return []
            
    def get_available_indices(self):
        """Get list of available RAG indices"""
        try:
            logger.info("Getting available RAG indices")
            indices = self.rag_handler.get_available_indices()
            if indices:
                logger.info(f"Found {len(indices)} indices")
                return [idx['name'] for idx in indices]
            logger.warning("No indices found, using default")
            return ["Default"]
        except Exception as e:
            logger.error(f"Error getting indices: {str(e)}", exc_info=True)
            return ["Default"]
            
    async def handle_model_change(self, model_name: str) -> Dict[str, Any]:
        """Handle model selection change"""
        try:
            logger.info(f"Handling model change to: {model_name}")
            if not model_name:
                logger.warning("No model selected")
                return {"status": "error", "message": "No model selected"}
                
            result = self.model_handler.set_model(model_name)
            logger.info(f"Model set to: {model_name}")
            return {"status": "success", "message": f"Model set to: {model_name}"}
            
        except Exception as e:
            logger.error(f"Error changing model: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
            
    async def handle_rag_change(self, index_name: str) -> Dict[str, Any]:
        """Handle RAG index selection change"""
        try:
            logger.info(f"Handling RAG index change to: {index_name}")
            if not index_name:
                logger.warning("No index selected")
                return {"status": "error", "message": "No index selected"}
                
            if index_name == "Default":
                logger.info("Using default RAG index")
                return {"status": "success", "message": "Using default RAG index"}
                
            self.rag_handler._load_index(index_name)
            logger.info(f"RAG index set to: {index_name}")
            return {"status": "success", "message": f"RAG index set to: {index_name}"}
            
        except Exception as e:
            logger.error(f"Error changing RAG index: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
            
def create_model_rag_selector(
    model_handler,
    rag_handler,
    with_status: bool = True
) -> Tuple[gr.Dropdown, gr.Dropdown, gr.Textbox]:
    """Create reusable model and RAG selection components"""
    
    selector = ModelRAGSelector(model_handler, rag_handler)
    
    with gr.Row():
        with gr.Column():
            model_dropdown = gr.Dropdown(
                choices=selector.get_available_models(),
                label="🤖 Select AI Model",
                value=selector.get_available_models()[0] if selector.get_available_models() else None,
                interactive=True
            )
            
        with gr.Column():
            rag_dropdown = gr.Dropdown(
                choices=selector.get_available_indices(),
                label="📚 Select RAG Index",
                value=selector.get_available_indices()[0] if selector.get_available_indices() else None,
                interactive=True
            )
            
    # Add refresh buttons
    with gr.Row():
        with gr.Column():
            refresh_model = gr.Button("🔄 Refresh Models")
            
        with gr.Column():
            refresh_rag = gr.Button("🔄 Refresh Indices")
            
    # Status message for feedback
    status_box = gr.Textbox(
        label="Status",
        interactive=False,
        visible=with_status
    ) if with_status else None
    
    # Event handlers
    def refresh_models():
        choices = selector.get_available_models()
        return gr.update(choices=choices, value=choices[0] if choices else None)
        
    def refresh_indices():
        choices = selector.get_available_indices()
        return gr.update(choices=choices, value=choices[0] if choices else None)
        
    # Connect events
    refresh_model.click(
        fn=refresh_models,
        outputs=[model_dropdown]
    )
    
    refresh_rag.click(
        fn=refresh_indices,
        outputs=[rag_dropdown]
    )
    
    if with_status:
        # Model change handler
        model_dropdown.change(
            fn=selector.handle_model_change,
            inputs=[model_dropdown],
            outputs=[status_box]
        )
        
        # RAG change handler
        rag_dropdown.change(
            fn=selector.handle_rag_change,
            inputs=[rag_dropdown],
            outputs=[status_box]
        )
        
    return model_dropdown, rag_dropdown, status_box