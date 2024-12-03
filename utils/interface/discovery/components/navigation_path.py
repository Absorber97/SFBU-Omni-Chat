import gradio as gr
from typing import Dict, Any, List

class NavigationPath:
    """Navigation path component for Discovery Mode"""
    
    def create(self) -> Dict[str, Any]:
        """Create navigation path component"""
        with gr.Accordion("🧭 Current Path", open=False, elem_classes=["path-container"]) as container:
            path = gr.Markdown(
                elem_classes=["path-content"]
            )

        return {
            "container": container,
            "path": path
        }
    
    def update(self, path_items: List[str]) -> str:
        """Update navigation path display"""
        if not path_items:
            return "Home"
        
        path_html = []
        for i, item in enumerate(path_items):
            if i > 0:
                path_html.append('<span class="path-arrow">→</span>')
            path_html.append(f'<span class="path-step">{item}</span>')
        
        return " ".join(path_html)