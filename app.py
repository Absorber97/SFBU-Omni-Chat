import gradio as gr
from core.app import SFBUApp
from core.handlers.data_handler import DataHandler
from core.handlers.model_handler import ModelHandler
from utils.interface_creator import create_interface

def main():
    app = SFBUApp()
    data_handler = DataHandler(app)
    model_handler = ModelHandler(app)
    
    interface = create_interface(app, data_handler, model_handler)
    interface.launch()

if __name__ == "__main__":
    main() 