import gradio as gr
from typing import Dict, Any, List

class CategorySelector:
    """Category selector component for Discovery Mode"""
    
    CATEGORIES = {
        "Academic Programs 🎓": [
            "Undergraduate Programs",
            "Graduate Programs",
            "Professional Certificates",
            "Research Opportunities"
        ],
        "Student Life 🌟": [
            "Campus Housing",
            "Student Organizations",
            "Events & Activities",
            "Health & Wellness"
        ],
        "Resources & Support 🛠️": [
            "Academic Support",
            "Career Services",
            "IT Services",
            "Financial Aid"
        ],
        "Campus Services 🏛️": [
            "Library",
            "Dining Services",
            "Transportation",
            "Safety & Security"
        ]
    }
    
    def create(self) -> Dict[str, Any]:
        """Create the category selector component"""
        with gr.Column(elem_classes=["category-selector"]) as container:
            gr.Markdown("### Browse by Category")
            
            # Main category dropdown
            category = gr.Dropdown(
                choices=list(self.CATEGORIES.keys()),
                label="Select Category",
                elem_classes=["category-dropdown"]
            )
            
            # Subcategory dropdown
            subcategory = gr.Dropdown(
                choices=[],
                label="Select Topic",
                elem_classes=["subcategory-dropdown"]
            )
        
        return {
            "container": container,
            "category": category,
            "subcategory": subcategory
        }
    
    def _update_subcategories(self, category: str) -> List[str]:
        """Update subcategory choices based on selected category"""
        return self.CATEGORIES.get(category, []) 