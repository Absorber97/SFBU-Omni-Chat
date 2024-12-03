import gradio as gr
from typing import Dict, Any
from utils.interface.discovery.components.category_selector import CategorySelector
from utils.interface.discovery.components.content_display import ContentDisplay
from utils.interface.discovery.components.suggestion_chips import SuggestionChips
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
            
            # Unified suggestion chips
            suggestions = self.suggestion_chips.create()
            
            # Event handlers for both category and suggestion buttons
            all_buttons = suggestion_buttons + suggestions["buttons"]
            
            for button in all_buttons:
                button.click(
                    fn=self.discovery_handler.handle_suggestion_click,
                    inputs=[
                        button,
                        self.model_selector,
                        self.use_rag,
                        self.rag_selector
                    ],
                    outputs=[
                        content_components["summary"],
                        content_components["details"],
                        content_components["bullets"],
                        content_components["steps"],
                        content_components["faq"],
                        *suggestions["buttons"],  # Update all suggestion buttons
                        path_display["path"]
                    ]
                )
        
        return {
            "container": container,
            "content": content_components,
            "suggestions": suggestions,
            "path": path_display
        } 