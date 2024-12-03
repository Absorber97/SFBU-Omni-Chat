from typing import List, Dict, Any
import gradio as gr

# Core categories with emojis
CORE_CATEGORIES = {
    "Academic Journey 🎓": [
        "📚 Explore SFBU's cutting-edge degree programs and specializations",
        "🔬 Research opportunities and innovation labs at SFBU",
        "📝 Course registration and academic planning strategies",
        "📖 Library resources and digital learning tools"
    ],
    "Campus Life 🌟": [
        "🏠 Student housing options and residential life experience",
        "🎯 Student clubs and leadership opportunities",
        "🍽️ Campus dining and meal plan options",
        "🏃 Sports and recreational activities"
    ],
    "Career Development 💼": [
        "🌱 Internship programs and industry partnerships",
        "📈 Career counseling and professional development",
        "🤝 Networking events and alumni connections",
        "💡 Startup incubator and entrepreneurship support"
    ],
    "Student Support 🤝": [
        "🎯 Academic advising and tutoring services",
        "🌈 International student resources and support",
        "💪 Health and wellness programs",
        "💭 Counseling and mental health services"
    ],
    "Campus Resources 🏛️": [
        "🔧 Technology resources and IT support",
        "🚗 Transportation and parking information",
        "🏥 Health and safety services",
        "🎨 Arts and cultural programs"
    ]
}

def create_suggestion_chips() -> Dict[str, Any]:
    """Create suggestion chips for each category"""
    
    with gr.Column() as container:
        gr.Markdown("### 🎯 Explore SFBU")
        
        for category, suggestions in CORE_CATEGORIES.items():
            with gr.Group():
                gr.Markdown(f"#### {category}")
                with gr.Row():
                    buttons = [
                        gr.Button(
                            suggestion,
                            size="sm",
                            elem_classes=["suggestion-chip"]
                        ) for suggestion in suggestions
                    ]
    
    return {
        "container": container,
        "buttons": buttons
    }

def create_followup_chips(suggestions: List[str]) -> gr.Column:
    """Create follow-up suggestion chips"""
    
    with gr.Column() as container:
        gr.Markdown("### 🔍 Related Topics")
        with gr.Row():
            buttons = [
                gr.Button(
                    suggestion,
                    size="sm",
                    elem_classes=["followup-chip"]
                ) for suggestion in suggestions
            ]
    
    return container 