import gradio as gr
import os
from data_processor.source_tracker import SourceTracker

def create_interface(app, data_handler, model_handler):
    """Create Gradio interface with all components"""
    
    def update_logs():
        """Get real-time logs"""
        return app.logger.get_logs()
    
    def get_source_info():
        """Get information about processed and fine-tuned sources"""
        try:
            tracker = model_handler.source_tracker
            return {
                'processed_sources': tracker.get_processed_sources(),
                'fine_tuned_sources': tracker.get_fine_tuned_sources()
            }
        except Exception as e:
            return {'error': str(e)}
    
    # Get absolute paths to images
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sfbu_logo_path = os.path.join(current_dir, "assets", "images", "SFBU.jpeg")
    bayhawk_path = os.path.join(current_dir, "assets", "images", "Bayhawk.jpeg")
    
    # Convert image path to data URL
    def get_image_data_url(image_path):
        import base64
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/jpeg;base64,{encoded_string}"

    sfbu_logo_data_url = get_image_data_url(sfbu_logo_path)
    
    with gr.Blocks(title="SFBU Omni Chat") as interface:
        # Header with logo
        gr.Markdown(f"""
            <div class="header-row">
                <div class="sfbu-logo-container">
                    <img src="{sfbu_logo_data_url}" class="sfbu-logo" alt="SFBU Logo">
                </div>
                <h1 class="header-title">Your SFBU Omni Assistant</h1>
            </div>
            <style>
            .header-row {{
                display: flex;
                align-items: center;
                gap: 20px;
                padding: 10px 20px;                
                border-bottom: 2px solid #003366;
            }}
            .sfbu-logo {{
                width: 64px !important;
                height: 64px !important;
                object-fit: contain !important;
            }}
            .header-title {{
                margin: 0 !important;
                padding: 0 !important;
            }}
            </style>
        """)

        with gr.Tab("🔄 Data Processing"):
            with gr.Row():
                with gr.Column():
                    pdf_input = gr.File(label="📒 Upload PDF")
                    process_pdf_btn = gr.Button("📥 Process PDF")
                    url_input = gr.Textbox(label="🔗 Enter URL")
                    process_url_btn = gr.Button("🌐 Process URL")
            
            with gr.Row():
                with gr.Column():
                    process_output = gr.JSON(label="📊 Processing Result")
                    log_output = gr.Textbox(label="📝 Processing Logs", lines=10)
                with gr.Column():
                    sources_display = gr.JSON(
                        label="📚 Data Sources",
                        value=get_source_info()
                    )
                    refresh_sources = gr.Button("🔄 Refresh Sources")
            
            with gr.Row():
                with gr.Column():
                    train_preview = gr.Dataframe(
                        headers=["prompt", "completion"],
                        label="🎯 Training Data Preview"
                    )
                    val_preview = gr.Dataframe(
                        headers=["prompt", "completion"],
                        label="✅ Validation Data Preview"
                    )

        with gr.Tab("🤖 Fine-tuning"):
            with gr.Row():
                with gr.Column():
                    training_file = gr.File(label="📄 Select Training File")
                    start_training_btn = gr.Button("🚀 Start Fine-tuning")
                    job_id_input = gr.Textbox(label="🔍 Job ID")
                    check_status_btn = gr.Button("📊 Check Status")
                with gr.Column():
                    training_output = gr.JSON(label="📈 Training Status")
                    status_output = gr.JSON(label="🔄 Current Status")
                    available_models = gr.Dropdown(
                        label="📚 Available Models",
                        choices=model_handler.load_available_models(),
                        interactive=True
                    )
                    refresh_models_btn = gr.Button("🔄 Refresh Models")

        with gr.Tab("💬 Chat"):
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
        refresh_sources.click(
            fn=get_source_info,
            outputs=[sources_display]
        )

        process_pdf_btn.click(
            fn=data_handler.process_pdf,
            inputs=[pdf_input],
            outputs=[process_output, train_preview, val_preview]
        ).then(
            fn=update_logs,
            outputs=[log_output]
        ).then(
            fn=get_source_info,
            outputs=[sources_display]
        )

        process_url_btn.click(
            fn=data_handler.process_url,
            inputs=[url_input],
            outputs=[process_output, train_preview, val_preview]
        ).then(
            fn=update_logs,
            outputs=[log_output]
        ).then(
            fn=get_source_info,
            outputs=[sources_display]
        )

        # Event handlers for Fine-tuning tab
        start_training_btn.click(
            fn=model_handler.start_fine_tuning,
            inputs=[training_file],
            outputs=[training_output]
        )

        check_status_btn.click(
            fn=model_handler.check_fine_tuning_status,
            inputs=[job_id_input],
            outputs=[status_output]
        )

        refresh_models_btn.click(
            fn=model_handler.load_available_models,
            outputs=[available_models, model_selector]  # Update both dropdowns
        )

        # Event handlers for Chat tab
        def send_message(message, history, model_id):
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

    return interface 