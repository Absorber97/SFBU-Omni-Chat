import gradio as gr
from typing import Any, Dict, List, Tuple

def create_chat_tab(app: Any, model_handler: Any, rag_handler: Any) -> gr.Tab:
    """Create the Chat tab components with RAG integration"""
    user_avatar, assistant_avatar = app.chat_styling.get_avatars()
    
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

    def send_message(message: str, history: List[Tuple[str, str]], 
                    model_id: str, use_rag: bool, rag_index: str) -> Tuple[List[Tuple[str, str]], Dict]:
        if not message.strip():
            return history, {"error": "Please enter a message"}
            
        if not model_id:
            return history, {"error": "Please select a model first"}
        
        if use_rag and not rag_index:
            return history, {"error": "Please select a RAG index first"}
            
        try:
            # First set the model in both handlers
            app.chat_manager.set_model(model_id)  # No need to check status as it raises exceptions
            model_handler.select_model(model_id)  # Keep model handler in sync
            
            if use_rag:
                try:
                    # Ensure RAG index is loaded
                    rag_handler._load_index(rag_index)
                    contexts = rag_handler.get_relevant_context(message)
                    
                    if contexts:  # Only add context if we got relevant results
                        # Format contexts with scores for better context utilization
                        context_text = "\n\n".join([
                            f"Relevant context (confidence: {c['score']:.2f}):\n"
                            f"Q: {c['metadata']['question']}\n"
                            f"A: {c['metadata']['answer']}"
                            for c in contexts
                        ])
                        
                        system_message = (
                            "You are a helpful assistant for San Francisco Bay University. "
                            "Use the following relevant context to inform your response, "
                            "but maintain a natural conversational tone:\n\n"
                            f"{context_text}"
                        )
                    else:
                        system_message = "You are a helpful assistant for San Francisco Bay University."
                except Exception as e:
                    # If RAG fails, fall back to regular chat
                    system_message = "You are a helpful assistant for San Francisco Bay University."
                    app.logger.warning(f"RAG retrieval failed, falling back to regular chat: {str(e)}")
            else:
                system_message = "You are a helpful assistant for San Francisco Bay University."
            
            messages = [{"role": "system", "content": system_message}]
            
            # Add chat history and current message
            for human, ai in history:
                messages.extend([
                    {"role": "user", "content": human},
                    {"role": "assistant", "content": ai}
                ])
            messages.append({"role": "user", "content": message})
            
            try:
                # Generate response with appropriate temperature
                response = app.chat_manager.generate_response(
                    messages=messages,
                    temperature=0.7 if use_rag else 0.9
                )
                
                if response:
                    history.append((message, response))
                    return history, {"status": "success"}
                else:
                    return history, {"error": "Received empty response from model"}
                
            except Exception as e:
                return history, {"error": f"Error generating response: {str(e)}"}
            
        except Exception as e:
            return history, {"error": str(e)}

    with gr.Tab("💬 Chat") as tab:
        with gr.Column(scale=1):
            # Move RAG controls to top
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
            
            # Chat components (unchanged)
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
            
            system_info = gr.JSON(
                label="System Status",
                visible=True,
                scale=1
            )
            
            with gr.Row():
                chat_input = gr.Textbox(
                    label="Message",
                    placeholder="Type your message here...",
                    container=True,
                    scale=4,
                    elem_id="chat-input"
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)
                clear_btn = gr.Button("🗑️ Clear History", scale=1)

        # Event handlers
        send_btn.click(
            send_message,
            inputs=[chat_input, chat_history, model_selector, use_rag, rag_index_selector],
            outputs=[chat_history, system_info]
        )

        chat_input.submit(
            send_message,
            inputs=[chat_input, chat_history, model_selector, use_rag, rag_index_selector],
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

    return tab 