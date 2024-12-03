from typing import Dict, List, Any, Tuple, Optional
import gradio as gr
from core.handlers.premium_response_handler import PremiumResponseHandler
from utils.interface.components.model_rag_selector import create_model_rag_selector
from utils.types import UserRole, ChatMode
from utils.interface.discovery.discovery_handler import DiscoveryHandler
from utils.interface.discovery.components.discovery_container import DiscoveryContainer

def create_premium_chat_tab(app, model_handler, rag_handler):
    """Create the premium chat tab with role-based and discovery modes"""
    response_handler = PremiumResponseHandler(rag_handler)
    discovery_handler = DiscoveryHandler(model_handler, rag_handler)
    
    # Role-based avatars
    role_avatars = {
        "user": "assets/images/Bayhawk.jpeg",
        "student": "assets/images/Student.jpeg",
        "faculty": "assets/images/Faculty.jpeg",
        "staff": "assets/images/Staff.jpeg",
        "visitor": "assets/images/Visitor.jpeg"
    }
    
    # Categories for discovery mode
    categories = {
        "Academic": ["Programs", "Courses", "Research", "Library"],
        "Student Life": ["Housing", "Activities", "Resources", "Support"],
        "Administration": ["Policies", "Procedures", "Forms", "Contact"],
        "Campus": ["Facilities", "Services", "Maps", "Safety"],
        "Career": ["Jobs", "Internships", "Development", "Alumni"]
    }
    
    def switch_mode(mode: str) -> Tuple[Any, Any]:
        """Switch between chat and discovery modes"""
        if mode == ChatMode.CHAT.value:
            return (
                gr.update(visible=True),  # chat container
                gr.update(visible=False)   # discovery container
            )
        else:
            return (
                gr.update(visible=False),  # chat container
                gr.update(visible=True)    # discovery container
            )
    
    with gr.Tab("🔮 Premium Chat"):
        with gr.Column():
            # RAG Configuration
            with gr.Group():
                gr.Markdown("### 🔍 RAG Configuration")
                with gr.Row():
                    use_rag = gr.Checkbox(
                        label="🔍 Enable RAG",
                        value=True,
                        info="Enable context-aware responses using RAG",
                        scale=1
                    )
                    rag_status = gr.JSON(
                        label="Active RAG Index",
                        value={"active_index": rag_handler.get_active_index() or "None"},
                        visible=True,
                        scale=2
                    )
            
            # Model and RAG selectors
            with gr.Row():
                with gr.Column(scale=3):
                    model_selector = gr.Dropdown(
                        label="🤖 Select AI Model",
                        choices=model_handler.load_available_models(),
                        interactive=True,
                        container=True
                    )
                    model_refresh_btn = gr.Button("🔄", scale=1, min_width=50)
                
                with gr.Column(scale=3):
                    rag_index_selector = gr.Dropdown(
                        label="📚 Select RAG Index",
                        choices=[idx['name'] for idx in rag_handler.get_available_indices()],
                        value=rag_handler.get_active_index(),
                        interactive=True,
                        container=True
                    )
                    rag_refresh_btn = gr.Button("🔄", scale=1, min_width=50)
            
            # System info
            system_info = gr.JSON(
                label="System Status",
                visible=True
            )
            
            # Mode toggle
            mode_toggle = gr.Radio(
                choices=[mode.value for mode in ChatMode],
                label="Select Mode",
                value=ChatMode.CHAT.value,
                interactive=True,
                elem_id="mode-toggle"
            )
            
            # Chat Mode Container
            with gr.Column(visible=True) as chat_container:
                # Role selector
                role = gr.Radio(
                    choices=[role.value for role in UserRole],
                    label="Select Your Role",
                    value=UserRole.STUDENT.value,
                    interactive=True
                )
                
                # Chat interface with avatars
                chatbot = gr.Chatbot(
                    label="Premium SFBU Assistant",
                    bubble_full_width=False,
                    height=400,
                    avatar_images=(role_avatars["user"], role_avatars[UserRole.STUDENT.value])
                )
                
                # Update avatar when role changes
                def update_avatar(role):
                    return gr.update(avatar_images=(role_avatars["user"], role_avatars[role]))
                
                role.change(
                    fn=update_avatar,
                    inputs=[role],
                    outputs=[chatbot]
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        label="Type your message here",
                        placeholder="Ask me anything about SFBU...",
                        lines=2,
                        scale=8
                    )
                    
                    with gr.Column(scale=1):
                        send = gr.Button("Send 📤", variant="primary")
                        clear = gr.Button("Clear 🗑️")
            
            # Discovery Mode Container
            discovery_container = DiscoveryContainer(discovery_handler).create()
            
            async def handle_chat(
                message: str,
                chat_history: List[List[str]],
                role: str,
                model_name: str,
                use_rag: bool,
                rag_index: str
            ) -> Tuple[str, List[List[str]], Dict[str, Any]]:
                """Handle chat messages"""
                if not message:
                    return "", chat_history, {
                        "outputs": {},
                        "status": "error",
                        "has_rag": False,
                        "error": "Please enter a message"
                    }
                
                if not model_name:
                    return "", chat_history, {
                        "outputs": {},
                        "status": "error",
                        "has_rag": False,
                        "error": "Please select a model first"
                    }
                
                if use_rag and not rag_index:
                    return "", chat_history, {
                        "outputs": {},
                        "status": "error",
                        "has_rag": False,
                        "error": "Please select a RAG index first"
                    }
                
                try:
                    # Convert chat history to tuple format
                    history_tuples = [(msg[0], msg[1]) for msg in chat_history]
                    
                    # Generate response with RAG integration
                    result = await response_handler.handle_chat_message(
                        message=message,
                        role=role,
                        history=history_tuples,
                        model_name=model_name,
                        use_rag=use_rag,
                        rag_index=rag_index
                    )
                    
                    if result["status"] == "success":
                        chat_history.append([message, result["response"]])
                        return "", chat_history, {
                            "outputs": {},
                            "status": "success",
                            "has_rag": result["has_rag_context"],
                            "error": None
                        }
                    else:
                        return "", chat_history, {
                            "outputs": {},
                            "status": "error",
                            "has_rag": result["has_rag_context"],
                            "error": result["error"]
                        }
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    return "", chat_history, {
                        "outputs": {},
                        "status": "error",
                        "has_rag": False,
                        "error": error_msg
                    }
            
            # Connect event handlers
            send.click(
                fn=handle_chat,
                inputs=[msg, chatbot, role, model_selector, use_rag, rag_index_selector],
                outputs=[msg, chatbot, system_info]
            )
            
            msg.submit(
                fn=handle_chat,
                inputs=[msg, chatbot, role, model_selector, use_rag, rag_index_selector],
                outputs=[msg, chatbot, system_info]
            )
            
            clear.click(
                fn=lambda: (None, None, {"status": "cleared"}),
                outputs=[msg, chatbot, system_info]
            )
            
            # Mode switching handler
            mode_toggle.change(
                fn=switch_mode,
                inputs=[mode_toggle],
                outputs=[chat_container, discovery_container["container"]]
            )
            
            # Model and RAG selection handlers
            model_selector.change(
                fn=model_handler.select_model,
                inputs=[model_selector],
                outputs=[system_info]
            )
            
            rag_index_selector.change(
                fn=lambda idx: {"active_index": idx},
                inputs=[rag_index_selector],
                outputs=[rag_status]
            )
            
            model_refresh_btn.click(
                fn=lambda: gr.update(choices=model_handler.load_available_models()),
                outputs=[model_selector]
            )
            
            rag_refresh_btn.click(
                fn=lambda: gr.update(
                    choices=[idx['name'] for idx in rag_handler.get_available_indices()]
                ),
                outputs=[rag_index_selector]
            )
            
            return chat_container