import gradio as gr
from typing import Dict, Any, List, Optional

class SuggestionChips:
    """Suggestion chips component for Discovery Mode"""
    
    def create(self, suggestions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create suggestion chips component"""
        if suggestions is None:
            suggestions = []
            
        with gr.Column(elem_classes=["suggestion-chips"]) as container:
            gr.Markdown("### 🔍 Related Topics")
            related = gr.Markdown(
                elem_classes=["content-text", "related-text"]
            )
        
        return {
            "container": container,
            "related": related
        }
    
    def update(self, suggestions: List[str]) -> List[Dict[str, Any]]:
        """Update suggestion chips with new suggestions"""
        return [
            {"value": suggestion, "visible": True}
            for suggestion in suggestions
        ]

class FollowupChips:
    """Followup suggestion chips component"""
    
    def create(self, suggestions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create followup chips component"""
        if suggestions is None:
            suggestions = []
            
        with gr.Column(elem_classes=["followup-chips"]) as container:
            gr.Markdown("### 🤔 Follow-up Questions")
            followups = gr.Markdown(
                elem_classes=["content-text", "followups-text"]
            )
        
        return {
            "container": container,
            "followups": followups
        }
    
    def update(self, suggestions: List[str]) -> List[Dict[str, Any]]:
        """Update followup chips with new suggestions"""
        return [
            {"value": suggestion, "visible": True}
            for suggestion in suggestions
        ] 