import gradio as gr
from typing import Any, Dict, List, Tuple

def create_chat_tab(app: Any, model_handler: Any) -> gr.Tab:
    """Create the Chat tab components"""
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

    with gr.Tab("💬 Chat") as tab:
        with gr.Row():
            with gr.Column():
                model_selector = gr.Dropdown(
                    label="🤖 Select Model",
                    choices=model_handler.load_available_models(),
                    interactive=True
                )
                chat_input = gr.Textbox(
                    label="💭 Your Message",
                    placeholder="Type your message here...",
                    lines=3
                )
                send_btn = gr.Button("📤 Send")
                clear_btn = gr.Button("🗑️ Clear History")
            with gr.Column():
                chat_history = gr.Chatbot(label="📜 Chat History")
                system_info = gr.JSON(label="ℹ️ System Info")

        # Event handlers
        send_btn.click(
            fn=send_message,
            inputs=[chat_input, chat_history, model_selector],
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

    return tab 