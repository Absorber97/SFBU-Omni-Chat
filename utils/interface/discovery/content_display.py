from typing import Dict, Any
import gradio as gr

def create_content_display() -> Dict[str, Any]:
    """Create structured content display for discovery mode"""
    
    with gr.Column() as container:
        # Quick Summary
        with gr.Accordion("📝 Quick Summary", open=True):
            summary = gr.Markdown()
        
        # Detailed Explanation
        with gr.Accordion("📚 Detailed Information", open=False):
            details = gr.Markdown()
        
        # Bullet Points
        with gr.Accordion("🔍 Key Points", open=False):
            bullets = gr.Markdown()
        
        # Step-by-Step Guide
        with gr.Accordion("📋 Step-by-Step Guide", open=False):
            steps = gr.Markdown()
        
        # FAQ Section
        with gr.Accordion("❓ Frequently Asked Questions", open=False):
            faq = gr.Markdown()
        
        # Path Visualization
        with gr.Accordion("🗺️ Navigation Path", open=True):
            path = gr.Markdown()
            
        # Interactive Elements Container
        with gr.Row():
            with gr.Column(scale=2):
                related = gr.Markdown("### 🔗 Related Topics")
            with gr.Column(scale=2):
                followups = gr.Markdown("### 📌 Follow-up Questions")
    
    return {
        "container": container,
        "summary": summary,
        "details": details,
        "bullets": bullets,
        "steps": steps,
        "faq": faq,
        "path": path,
        "related": related,
        "followups": followups
    }

def format_content(content: Dict[str, Any]) -> Dict[str, str]:
    """Format content for display"""
    return {
        "summary": f"### Summary\n{content.get('summary', '')}",
        "details": f"### Detailed Explanation\n{content.get('details', '')}",
        "bullets": "\n".join([f"• {point}" for point in content.get('bullets', [])]),
        "steps": "\n".join([f"{i+1}. {step}" for i, step in enumerate(content.get('steps', []))]),
        "faq": "\n\n".join([f"**Q: {q}**\nA: {a}" for q, a in content.get('faq', {}).items()]),
        "path": " → ".join(content.get('path', [])),
        "related": "\n".join([f"• {topic}" for topic in content.get('related', [])]),
        "followups": "\n".join([f"• {q}" for q in content.get('followups', [])])
    } 