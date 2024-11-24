import gradio as gr
from typing import Any, Dict, List, Tuple

def create_chat_tab(app: Any, model_handler: Any, rag_handler: Any) -> gr.Tab:
    """Create the Chat tab components with RAG integration"""
    # Get avatar configuration from styling directly
    user_avatar, assistant_avatar = app.chat_styling.get_avatars()
    
    def send_message(message: str, history: List[Tuple[str, str]], 
                    model_id: str, use_rag: bool) -> Tuple[List[Tuple[str, str]], Dict]:
        if not model_id:
            return history, {"error": "Please select a model first"}
        
        try:
            if use_rag:
                # Get relevant context from RAG
                contexts = rag_handler.get_relevant_context(message)
                
                # Format contexts with scores for better context utilization
                context_text = "\n\n".join([
                    f"Relevant context (confidence: {c['score']:.2f}):\n"
                    f"Q: {c['metadata']['question']}\n"
                    f"A: {c['metadata']['answer']}"
                    for c in contexts
                ])
                
                # Create a system message with context
                system_message = (
                    "You are a helpful assistant for San Francisco Bay University. "
                    "Use the following relevant context to inform your response, "
                    "but maintain a natural conversational tone:\n\n"
                    f"{context_text}"
                )
                
                # Format messages for the API with system context
                messages = [{"role": "system", "content": system_message}]
                
                # Add chat history
                for human, ai in history:
                    messages.extend([
                        {"role": "user", "content": human},
                        {"role": "assistant", "content": ai}
                    ])
                
                # Add current message
                messages.append({"role": "user", "content": message})
            else:
                # Without RAG, use default system message
                messages = [{"role": "system", "content": 
                    "You are a helpful assistant for San Francisco Bay University."}]
                
                # Add chat history and current message
                for human, ai in history:
                    messages.extend([
                        {"role": "user", "content": human},
                        {"role": "assistant", "content": ai}
                    ])
                messages.append({"role": "user", "content": message})
            
            # Get AI response using the selected model
            response = app.chat_manager.generate_response(
                messages=messages,
                model_id=model_id,
                temperature=0.7 if use_rag else 0.9  # Lower temperature with RAG for more focused responses
            )
            
            # Update history
            history.append((message, response))
            return history, {"status": "success"}
            
        except Exception as e:
            return history, {"error": str(e)}

    def refresh_models() -> gr.Dropdown:
        """Refresh available models list"""
        try:
            models = model_handler.load_available_models()
            return gr.Dropdown(choices=models, value=models[0] if models else None)
        except Exception as e:
            return gr.Dropdown(choices=["Error loading models"], value=None)

    with gr.Tab("💬 Chat") as tab:
        with gr.Column(scale=1):
            # Model selector with refresh button
            with gr.Row():
                model_selector = gr.Dropdown(
                    label="🤖 Select AI Model",
                    choices=model_handler.load_available_models(),
                    interactive=True,
                    container=True,
                    scale=4
                )
                refresh_btn = gr.Button(
                    "🔄", 
                    scale=1,
                    min_width=50
                )
            
            # Chat history with avatars
            chat_history = gr.Chatbot(
                label="Chat History",
                height=700,
                container=True,
                show_label=False,
                elem_id="chat-history",
                show_copy_button=True,
                avatar_images=(user_avatar, assistant_avatar),
                scale=1
            )
            
            # System info for status messages
            system_info = gr.JSON(
                label="System Status",
                visible=True,
                scale=1
            )
            
            # Input area
            with gr.Row():
                chat_input = gr.Textbox(
                    label="Message",
                    placeholder="Type your message here...",
                    container=True,
                    scale=4,
                    elem_id="chat-input"
                )
                send_btn = gr.Button(
                    "Send",
                    variant="primary",
                    scale=1,
                    elem_id="send-btn"
                )
                clear_btn = gr.Button(
                    "🗑️ Clear History",
                    scale=1
                )

        # Add RAG status and controls
        with gr.Group():
            gr.Markdown("### 🔍 RAG Status")
            rag_status = gr.JSON(
                label="Active RAG Index",
                value={"active_index": "None"},
                visible=True
            )
            
            use_rag = gr.Checkbox(
                label="🔍 Use RAG",
                value=True,
                info="Enable context-aware responses using RAG"
            )

        # Event handlers
        send_btn.click(
            send_message,
            inputs=[chat_input, chat_history, model_selector, use_rag],
            outputs=[chat_history, system_info]
        )

        chat_input.submit(
            send_message,
            inputs=[chat_input, chat_history, model_selector, use_rag],
            outputs=[chat_history, system_info]
        )

        clear_btn.click(
            fn=lambda: ([], {"status": "cleared"}),
            outputs=[chat_history, system_info]
        )

        model_selector.change(
            fn=model_handler.select_model,
            inputs=[model_selector],
            outputs=[system_info]
        )

        refresh_btn.click(
            fn=refresh_models,
            outputs=[model_selector]
        )

    return tab 