import gradio as gr
from typing import Dict, Any
from utils.interface.discovery.components.category_selector import CategorySelector
from utils.interface.discovery.components.content_display import ContentDisplay
from utils.interface.discovery.components.suggestion_chips import SuggestionChips, FollowupChips
from utils.interface.discovery.components.navigation_path import NavigationPath

class DiscoveryContainer:
    """Modern Discovery Mode container component"""
    
    def __init__(self, discovery_handler):
        self.discovery_handler = discovery_handler
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
            category_components = self.category_selector.create()
            
            # Content sections
            content_components = self.content_display.create()
            
            # Suggestion chips
            with gr.Row():
                suggestion_components = self.suggestion_chips.create()
                followup_components = self.followup_chips.create()
            
            # Event handlers
            category_components["category"].change(
                fn=self.category_selector._update_subcategories,
                inputs=[category_components["category"]],
                outputs=[category_components["subcategory"]]
            )
            
            category_components["subcategory"].change(
                fn=self.discovery_handler.handle_suggestion_click,
                inputs=[
                    category_components["subcategory"],
                    gr.State("gpt-4"),  # Default model
                    gr.State(True)  # Use RAG by default
                ],
                outputs=[
                    content_components["summary"],
                    content_components["details"],
                    content_components["steps"],
                    content_components["faq"],
                    suggestion_components["container"],
                    followup_components["container"],
                    path_display["path"]
                ]
            )
        
        return {
            "container": container,
            "category": category_components["category"],
            "subcategory": category_components["subcategory"],
            "content": content_components,
            "suggestions": suggestion_components,
            "followups": followup_components,
            "path": path_display
        } 