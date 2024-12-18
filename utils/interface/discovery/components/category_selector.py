import gradio as gr
from typing import Dict, Any, List, Tuple

class CategorySelector:
    """Category selector component for Discovery Mode"""
    
    CORE_CATEGORIES = {
        "Academic Excellence 🎓": [
            "🌟 Discover SFBU's cutting-edge degree programs and research opportunities",
            "📚 Explore our innovative curriculum and specialized courses",
            "🔬 Learn about our state-of-the-art research facilities and labs",
            "👩‍🏫 Meet our distinguished faculty and their expertise"
        ],
        "Student Journey 🌱": [
            "🏠 Experience vibrant campus life and housing options",
            "🎯 Join dynamic student clubs and leadership programs",
            "🌍 International student support and cultural integration",
            "💪 Access comprehensive health and wellness resources"
        ],
        "Career Development 💼": [
            "🚀 Launch your career with our industry partnerships",
            "💡 Explore entrepreneurship and startup opportunities",
            "🤝 Connect with our alumni network and mentorship programs",
            "📈 Access career counseling and professional development"
        ],
        "Campus Resources 🏛️": [
            "📖 Discover our modern library and digital learning tools",
            "🖥️ Access cutting-edge technology and IT support",
            "🚗 Learn about transportation and campus accessibility",
            "🏥 Explore health services and safety measures"
        ],
        "Community & Support 🤝": [
            "🎯 Get personalized academic advising and tutoring",
            "💰 Learn about financial aid and scholarship options",
            "🌈 Access diversity and inclusion initiatives",
            "🤗 Mental health and counseling support services"
        ]
    }
    
    def create(self) -> Tuple[gr.Column, List[gr.Button]]:
        """Create the category selector component"""
        suggestion_buttons = []
        
        with gr.Column(elem_classes=["category-selector"]) as container:
            gr.Markdown("### 🎯 Explore SFBU")
            
            # Create category sections in a grid layout
            for category, suggestions in self.CORE_CATEGORIES.items():
                with gr.Group(elem_classes=["category-section"]):
                    gr.Markdown(f"### {category}", elem_classes=["category-title"])
                    
                    # Create a 2x2 grid for suggestions
                    with gr.Row(equal_height=True):
                        for i in range(0, len(suggestions), 2):
                            with gr.Column(scale=1):
                                for j in range(2):
                                    if i + j < len(suggestions):
                                        button = gr.Button(
                                            value=suggestions[i + j],
                                            elem_classes=["category-button"],
                                            variant="secondary",
                                            size="lg"
                                        )
                                        suggestion_buttons.append(button)
        
        return container, suggestion_buttons
    
    def get_suggestions(self, category: str) -> List[str]:
        """Get suggestions for a category"""
        return self.CORE_CATEGORIES.get(category, [])