import gradio as gr
from typing import Dict, List, Optional, Any, Tuple
from config import MODEL_CONFIG
from core.handlers.premium_response_handler import PremiumResponseHandler
from utils.types import UserRole, ChatMode, ChatHistory
import json

def create_premium_chat_tab(app, model_handler, rag_handler):
    """Create the premium chat tab with role-based and discovery modes"""
    
    response_handler = PremiumResponseHandler(rag_handler)
    
    # Role-based avatars with emojis
    role_avatars = {
        UserRole.STUDENT.value: "👨‍🎓",
        UserRole.FACULTY.value: "👨‍🏫",
        UserRole.STAFF.value: "👨‍💼",
        UserRole.VISITOR.value: "👤"
    }
    
    # Categories for discovery mode
    categories = {
        "Academic": ["Programs", "Courses", "Research", "Library"],
        "Student Life": ["Housing", "Activities", "Resources", "Support"],
        "Administration": ["Policies", "Procedures", "Forms", "Contact"],
        "Campus": ["Facilities", "Services", "Maps", "Safety"],
        "Career": ["Jobs", "Internships", "Development", "Alumni"]
    }
    
    def refresh_rag_indices() -> Tuple[gr.Dropdown, Dict[str, Any]]:
        """Refresh available RAG indices"""
        try:
            indices = rag_handler.get_available_indices()
            index_choices = [idx['name'] for idx in indices]
            current_index = rag_handler.get_active_index()
            return (
                gr.Dropdown(choices=index_choices, value=current_index),
                {"active_index": current_index or "None"}
            )
        except Exception as e:
            return (
                gr.Dropdown(choices=[], value=None),
                {"active_index": "None", "error": str(e)}
            )
    
    def load_rag_index(index_name: str) -> Dict[str, Any]:
        """Load selected RAG index"""
        try:
            if not index_name:
                return {"active_index": "None", "status": "error", "message": "No index selected"}
            rag_handler._load_index(index_name)
            return {
                "active_index": index_name,
                "status": "success",
                "message": f"Successfully loaded index: {index_name}"
            }
        except Exception as e:
            return {
                "active_index": "None",
                "status": "error",
                "message": f"Error loading index: {str(e)}"
            }
    
    def switch_mode(mode: str):
        """Switch between chat and discovery modes"""
        if mode == ChatMode.CHAT.value:
            return {
                chat_container: gr.update(visible=True),
                discovery_container: gr.update(visible=False)
            }
        else:
            return {
                chat_container: gr.update(visible=False),
                discovery_container: gr.update(visible=True)
            }
    
    async def handle_chat(
        message: str,
        history: ChatHistory,
        role: str,
        model_name: str,
        use_rag: bool,
        rag_index: str
    ) -> Tuple[str, ChatHistory, Dict[str, Any]]:
        """Handle chat messages"""
        if not message:
            return "", history, {"error": "Please enter a message"}
            
        if not model_name:
            return "", history, {"error": "Please select a model first"}
            
        if use_rag and not rag_index:
            return "", history, {"error": "Please select a RAG index first"}
            
        try:
            # Set the model
            model_handler.select_model(model_name)
            
            # Get RAG context if enabled
            context_text = None
            if use_rag:
                try:
                    rag_handler._load_index(rag_index)
                    contexts = rag_handler.get_relevant_context(message)
                    if contexts:
                        context_text = "\n\n".join([
                            f"Relevant context (confidence: {c['score']:.2f}):\n"
                            f"Q: {c['metadata']['question']}\n"
                            f"A: {c['metadata']['answer']}"
                            for c in contexts
                        ])
                except Exception as e:
                    print(f"RAG retrieval failed: {str(e)}")
            
            response = await response_handler.generate_chat_response(
                query=message,
                role=role,
                history=history,
                context=context_text
            )
            
            history.append((message, response))
            return "", history, {"status": "success"}
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            return "", history, {"error": error_msg}
    
    async def handle_discovery(
        category: str,
        subcategory: str,
        model_name: str,
        use_rag: bool,
        rag_index: str
    ) -> Dict[str, Any]:
        """Handle discovery mode interactions"""
        try:
            # Set the model
            model_handler.select_model(model_name)
            
            # Get RAG context if enabled
            context_text = None
            if use_rag and rag_index:
                try:
                    rag_handler._load_index(rag_index)
                    contexts = rag_handler.get_relevant_context(f"{category} {subcategory}")
                    if contexts:
                        context_text = "\n\n".join([c['content'] for c in contexts])
                except Exception as e:
                    print(f"RAG retrieval failed: {str(e)}")
            
            content = await response_handler.generate_discovery_content(
                f"{category} - {subcategory}",
                context=context_text
            )
            
            return {
                summary_box: content["summary"],
                detailed_box: content["detailed"],
                steps_box: content["steps"],
                faq_box: content["faq"],
                suggestions_box: gr.update(choices=content["suggestions"]),
                followups_box: gr.update(choices=content["followups"]),
                system_info: {"status": "success"}
            }
            
        except Exception as e:
            error_content = {
                "summary": f"Error: {str(e)}",
                "detailed": "An error occurred",
                "steps": "",
                "faq": "",
                "suggestions": [],
                "followups": []
            }
            return {
                summary_box: error_content["summary"],
                detailed_box: error_content["detailed"],
                steps_box: error_content["steps"],
                faq_box: error_content["faq"],
                suggestions_box: gr.update(choices=error_content["suggestions"]),
                followups_box: gr.update(choices=error_content["followups"]),
                system_info: {"error": str(e)}
            }
    
    with gr.Tab("Premium Chat"):
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
                
                # Chat interface
                chatbot = gr.Chatbot(
                    label="Premium SFBU Assistant",
                    bubble_full_width=False,
                    height=400
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
                
                # Event handlers
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
                
            # Discovery Mode Container
            with gr.Column(visible=False) as discovery_container:
                # Category selection
                with gr.Row():
                    category = gr.Dropdown(
                        choices=list(categories.keys()),
                        label="Select Category",
                        interactive=True
                    )
                    
                    subcategory = gr.Dropdown(
                        choices=[],
                        label="Select Topic",
                        interactive=True
                    )
                
                # Content display
                with gr.Column() as content_display:
                    with gr.Accordion("Quick Summary", open=True):
                        summary_box = gr.Markdown()
                    
                    with gr.Accordion("Detailed Information", open=False):
                        detailed_box = gr.Markdown()
                    
                    with gr.Accordion("Step-by-Step Guide", open=False):
                        steps_box = gr.Markdown()
                    
                    with gr.Accordion("FAQ", open=False):
                        faq_box = gr.Markdown()
                    
                    with gr.Row():
                        with gr.Column():
                            suggestions_box = gr.Radio(
                                choices=[],
                                label="Related Topics",
                                interactive=True
                            )
                        
                        with gr.Column():
                            followups_box = gr.Radio(
                                choices=[],
                                label="Follow-up Questions",
                                interactive=True
                            )
                
                # Event handlers
                def update_subcategories(cat):
                    return gr.update(choices=categories[cat])
                    
                category.change(
                    fn=update_subcategories,
                    inputs=[category],
                    outputs=[subcategory]
                )
                
                subcategory.change(
                    fn=handle_discovery,
                    inputs=[category, subcategory, model_selector, use_rag, rag_index_selector],
                    outputs=[
                        summary_box,
                        detailed_box,
                        steps_box,
                        faq_box,
                        suggestions_box,
                        followups_box,
                        system_info
                    ]
                )
            
            # Mode switching handler
            mode_toggle.change(
                fn=switch_mode,
                inputs=[mode_toggle],
                outputs=[chat_container, discovery_container]
            )
            
            # Model and RAG selection handlers
            model_selector.change(
                fn=model_handler.select_model,
                inputs=[model_selector],
                outputs=[system_info]
            )
            
            rag_index_selector.change(
                fn=load_rag_index,
                inputs=[rag_index_selector],
                outputs=[rag_status]
            )
            
            model_refresh_btn.click(
                fn=lambda: gr.Dropdown(choices=model_handler.load_available_models()),
                outputs=[model_selector]
            )
            
            rag_refresh_btn.click(
                fn=refresh_rag_indices,
                outputs=[rag_index_selector, rag_status]
            )