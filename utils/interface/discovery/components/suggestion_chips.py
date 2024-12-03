import gradio as gr
from typing import Dict, Any, List, Optional

class SuggestionChips:
    """Interactive suggestion chips component for Discovery Mode"""
    
    def create(self, suggestions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create interactive suggestion chips component"""
        if suggestions is None:
            suggestions = []
            
        with gr.Column(elem_classes=["suggestion-section"]) as container:
            gr.Markdown("### 🔍 Explore Related Topics", elem_classes=["category-title"])
            
            # Create buttons in a 2-column grid layout
            with gr.Row(elem_classes=["suggestion-grid"]):
                # First column
                with gr.Column(scale=1):
                    suggestion_buttons_left = [
                        gr.Button(
                            "Loading suggestions...",
                            elem_classes=["category-button", "suggestion-button"],
                            visible=False
                        ) for _ in range(4)  # 4 buttons in left column
                    ]
                
                # Second column
                with gr.Column(scale=1):
                    suggestion_buttons_right = [
                        gr.Button(
                            "Loading suggestions...",
                            elem_classes=["category-button", "suggestion-button"],
                            visible=False
                        ) for _ in range(4)  # 4 buttons in right column
                    ]
        
        return {
            "container": container,
            "buttons": suggestion_buttons_left + suggestion_buttons_right
        }
    
    def update(self, suggestions: List[str]) -> List[Dict[str, Any]]:
        """Update suggestion buttons with new suggestions"""
        # Ensure we have exactly 8 updates (show/hide as needed)
        updates = []
        for i in range(8):
            if i < len(suggestions):
                updates.append({
                    "value": suggestions[i],
                    "visible": True
                })
            else:
                updates.append({
                    "value": "",
                    "visible": False
                })
        return updates 