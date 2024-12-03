import gradio as gr
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ContentDisplay:
    """Content display component for Discovery Mode"""
    
    def create(self) -> Dict[str, Any]:
        """Create content display component"""
        components = {}
        
        with gr.Column(elem_classes=["content-display"]) as container:
            # Quick Summary Section
            with gr.Accordion("🎯 Quick Summary", open=True, elem_classes=["summary-section"]):
                components["summary"] = gr.Markdown(
                    elem_classes=["content-text", "summary-text"],
                    show_label=False
                )

            # Detailed Information Section
            with gr.Accordion("📚 Detailed Information", open=True, elem_classes=["details-section"]):
                components["details"] = gr.Markdown(
                    elem_classes=["content-text", "details-text"],
                    show_label=False
                )
            
            # Key Points Section
            with gr.Accordion("🔑 Key Points", open=True, elem_classes=["bullets-section"]):
                components["bullets"] = gr.Markdown(
                    elem_classes=["content-text", "bullets-text"],
                    show_label=False
                )
            
            # Steps Section
            with gr.Accordion("📝 Step-by-Step Guide", open=True, elem_classes=["steps-section"]):
                components["steps"] = gr.Markdown(
                    elem_classes=["content-text", "steps-text"],
                    show_label=False
                )
            
            # FAQ Section
            with gr.Accordion("❓ Frequently Asked Questions", open=True, elem_classes=["faq-section"]):
                components["faq"] = gr.Markdown(
                    elem_classes=["content-text", "faq-text"],
                    show_label=False
                )
        
        components["container"] = container
        return components

    @staticmethod
    def format_summary(text: str) -> str:
        """Format summary text"""
        logger.info(f"Formatting summary: {text[:100]}...")
        return text.strip()

    @staticmethod
    def format_details(text: str) -> str:
        """Format detailed information with proper markdown"""
        logger.info(f"Formatting details: {text[:100]}...")
        # Ensure headers and formatting are preserved
        return text.strip()

    @staticmethod
    def format_bullets(points: list) -> str:
        """Format bullet points properly"""
        logger.info(f"Formatting {len(points)} bullet points")
        formatted = "\n".join(f"• {point.strip()}" for point in points)
        return formatted

    @staticmethod
    def format_steps(steps: list) -> str:
        """Format step-by-step guide properly"""
        logger.info(f"Formatting {len(steps)} steps")
        formatted = "\n".join(f"{i+1}. {step.strip()}" for i, step in enumerate(steps))
        return formatted

    @staticmethod
    def format_faq(faqs: list) -> str:
        """Format FAQ with proper Q&A structure"""
        logger.info(f"Formatting {len(faqs)} FAQ items")
        formatted_faqs = []
        for qa in faqs:
            q = qa.get('question', '').strip()
            a = qa.get('answer', '').strip()
            formatted_faqs.append(f"**Q: {q}**\n\nA: {a}\n")
        return "\n---\n".join(formatted_faqs)