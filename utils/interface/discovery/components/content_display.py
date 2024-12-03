import gradio as gr
from typing import Dict, Any

class ContentDisplay:
    """Content display component for Discovery Mode"""
    
    def create(self) -> Dict[str, Any]:
        """Create content display component"""
        components = {}
        
        with gr.Column(elem_classes=["content-display"]) as container:
            # Quick Summary Section
            with gr.Accordion("🎯 Quick Summary", open=False, elem_classes=["summary-section"]):
                components["summary"] = gr.Markdown(
                    elem_classes=["content-text", "details-text"]
                )

            # Detailed Information Section
            with gr.Accordion("📚 Detailed Information", open=False, elem_classes=["details-section"]):
                components["details"] = gr.Markdown(
                    elem_classes=["content-text", "details-text"]
                )
            
            # Key Points Section
            with gr.Accordion("🔑 Key Points", open=False, elem_classes=["bullets-section"]):
                components["bullets"] = gr.Markdown(
                    elem_classes=["content-text", "bullets-text"]
                )
            
            # Steps Section
            with gr.Accordion("📝 Step-by-Step Guide", open=False, elem_classes=["steps-section"]):
                components["steps"] = gr.Markdown(
                    elem_classes=["content-text", "steps-text"]
                )
            
            # FAQ Section
            with gr.Accordion("❓ Frequently Asked Questions", open=False, elem_classes=["faq-section"]):
                components["faq"] = gr.Markdown(
                    elem_classes=["content-text", "faq-text"]
                )
            
            # Related Topics Section
            with gr.Row():
                with gr.Column(scale=1):
                    
                    components["related"] = gr.Markdown(
                        elem_classes=["content-text", "related-text"]
                    )
                
                with gr.Column(scale=1):
                    
                    components["followups"] = gr.Markdown(
                        elem_classes=["content-text", "followups-text"]
                    )
        
        components["container"] = container
        return components 