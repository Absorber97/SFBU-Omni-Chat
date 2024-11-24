import gradio as gr
from typing import Any, Dict, List, Tuple

def create_chat_tab(app: Any, model_handler: Any) -> gr.Tab:
    """Create the Chat tab components"""
    # Get avatar configuration from styling directly
    user_avatar, assistant_avatar = app.chat_styling.get_avatars()
    
    def send_message(message: str, history: List[Tuple[str, str]], model_id: str) -> Tuple[List[Tuple[str, str]], Dict]:
        if not model_id:
            return history, {"error": "Please select a model first"}
        
        try:
            # Format messages for the API
            messages = []
            for human, ai in history:
                messages.extend([
                    {"role": "user", "content": human},
                    {"role": "assistant", "content": ai}
                ])
            messages.append({"role": "user", "content": message})
            
            # Get AI response
            response = app.chat_manager.generate_response(messages)
            
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
        # Single column layout for better chat experience
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
            
            # Input area at the bottom
            with gr.Row():
                chat_input = gr.Textbox(
                    placeholder="Type your message here...",
                    show_label=False,
                    container=False,
                    scale=4,
                    elem_id="chat-input"
                )
                send_btn = gr.Button(
                    "Send",
                    variant="primary",
                    scale=1,
                    elem_id="send-btn"
                )
            
            # Additional controls in a row
            with gr.Row():
                clear_btn = gr.Button(
                    "🗑️ Clear History",
                    variant="secondary",
                    scale=1
                )
                system_info = gr.JSON(
                    label="System Status",
                    visible=True,
                    scale=1
                )

        # Add custom CSS for better styling
        gr.HTML("""
            <style>
                /* Chat container styles */
                #chat-history {
                    border-radius: 10px;
                    margin: 20px 0;
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
                }
                
                /* Message styles */
                .message {
                    padding: 12px;
                    margin: 8px 0;
                    border-radius: 8px;
                }
                
                /* Input area styles */
                #chat-input {
                    border-radius: 20px;
                    padding: 12px 20px;
                    margin: 10px 0;
                }
                
                /* Send button styles */
                #send-btn {
                    border-radius: 20px;
                    min-width: 100px;
                }
                
                /* Custom scrollbar */
                #chat-history::-webkit-scrollbar {
                    width: 8px;
                }
                #chat-history::-webkit-scrollbar-track {
                    background: #f1f1f1;
                    border-radius: 4px;
                }
                #chat-history::-webkit-scrollbar-thumb {
                    background: #888;
                    border-radius: 4px;
                }
                #chat-history::-webkit-scrollbar-thumb:hover {
                    background: #555;
                }
            </style>
        """)

        # Event handlers
        send_btn.click(
            fn=send_message,
            inputs=[chat_input, chat_history, model_selector],
            outputs=[chat_history, system_info]
        ).then(
            fn=lambda: "",  # Clear input after sending
            outputs=[chat_input]
        )

        # Enter key to send
        chat_input.submit(
            fn=send_message,
            inputs=[chat_input, chat_history, model_selector],
            outputs=[chat_history, system_info]
        ).then(
            fn=lambda: "",  # Clear input after sending
            outputs=[chat_input]
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