import gradio as gr
from typing import Any, Callable

def create_fine_tuning_tab(model_handler: Any) -> gr.Tab:
    """Create the Fine-tuning tab components"""
    with gr.Tab("🤖 Fine-tuning") as tab:
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

        # Event handlers
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
            outputs=[available_models]
        )

    return tab 