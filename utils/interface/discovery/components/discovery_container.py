import gradio as gr
from typing import Dict, Any
from utils.interface.discovery.components.category_selector import CategorySelector
from utils.interface.discovery.components.content_display import ContentDisplay
from utils.interface.discovery.components.suggestion_chips import SuggestionChips, FollowupChips
from utils.interface.discovery.components.navigation_path import NavigationPath

class DiscoveryContainer:
    """Modern Discovery Mode container component"""
    
    def __init__(self, discovery_handler, model_selector, rag_selector, use_rag):
        self.discovery_handler = discovery_handler
        self.model_selector = model_selector
        self.rag_selector = rag_selector
        self.use_rag = use_rag
        self.category_selector = CategorySelector()
        self.content_display = ContentDisplay()
        self.suggestion_chips = SuggestionChips()
        self.followup_chips = FollowupChips()
        self.navigation_path = NavigationPath()
    
    def create(self) -> Dict[str, Any]:
        """Create the Discovery Mode container"""
        with gr.Column(visible=False, elem_classes=["discovery-container"]) as container:
            # Navigation path
            path_display = self.navigation_path.create()
            
            # Category selection
            category_container, suggestion_buttons = self.category_selector.create()
            
            # Content sections
            content_components = self.content_display.create()
            
            # Suggestion chips
            with gr.Row():
                suggestions = self.suggestion_chips.create()
                followups = self.followup_chips.create()
            
            # Event handlers for suggestion buttons
            for button in suggestion_buttons:
                button.click(
                    fn=self.discovery_handler.handle_suggestion_click,
                    inputs=[
                        button,
                        self.model_selector,  # Use selected model
                        self.use_rag,        # Use RAG setting
                        self.rag_selector    # Use selected RAG index
                    ],
                    outputs=[
                        content_components["summary"],     # Summary text
                        content_components["details"],     # Detailed text
                        content_components["bullets"],     # Bullet points
                        content_components["steps"],       # Step-by-step guide
                        content_components["faq"],         # FAQ section
                        suggestions["related"],           # Related topics
                        followups["followups"],          # Follow-up questions
                        path_display["path"]              # Navigation path
                    ]
                )
        
        return {
            "container": container,
            "content": content_components,
            "suggestions": suggestions,
            "followups": followups,
            "path": path_display
        } 