import gradio as gr
from core.app import SFBUApp
from core.handlers.data_handler import DataHandler
from core.handlers.model_handler import ModelHandler
from core.handlers.rag_handler import RAGHandler
from utils.interface_creator import create_interface
from config import OPENAI_API_KEY

def main():
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set in environment variables")
        
    app = SFBUApp()
    data_handler = DataHandler(app)
    model_handler = ModelHandler(app)
    rag_handler = RAGHandler(OPENAI_API_KEY)
    
    interface = create_interface(app, data_handler, model_handler, rag_handler)
    interface.launch()

if __name__ == "__main__":
    main() 