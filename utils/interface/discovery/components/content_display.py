import gradio as gr
from typing import Dict, Any

class ContentDisplay:
    """Content display component for Discovery Mode"""
    
    def create(self) -> Dict[str, Any]:
        """Create content display component"""
        components = {}
        
        with gr.Column(elem_classes=["content-display"]) as container:
            # Quick Summary Section
            with gr.Group(elem_classes=["content-section", "summary-section"]):
                gr.Markdown("### Quick Summary")
                components["summary"] = gr.Markdown(
                    elem_classes=["content-text", "summary-text"]
                )
            
            # Detailed Information Section
            with gr.Group(elem_classes=["content-section", "details-section"]):
                gr.Markdown("### Detailed Information")
                components["details"] = gr.Markdown(
                    elem_classes=["content-text", "details-text"]
                )
            
            # Steps Section (Collapsible)
            with gr.Accordion("Step-by-Step Guide", open=False, elem_classes=["steps-section"]):
                components["steps"] = gr.Markdown(
                    elem_classes=["content-text", "steps-text"]
                )
            
            # FAQ Section (Collapsible)
            with gr.Accordion("Frequently Asked Questions", open=False, elem_classes=["faq-section"]):
                components["faq"] = gr.Markdown(
                    elem_classes=["content-text", "faq-text"]
                )
        
        components["container"] = container
        return components 