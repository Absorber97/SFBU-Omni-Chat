import gradio as gr
from typing import Callable, Any

def create_data_processing_tab(
    data_handler: Any,
    update_logs: Callable,
    get_source_info: Callable
) -> gr.Tab:
    """Create the Data Processing tab components"""
    with gr.Tab("🔄 Data Processing") as tab:
        with gr.Row():
            with gr.Column():
                pdf_input = gr.File(label="📒 Upload PDF")
                process_pdf_btn = gr.Button("📥 Process PDF")
                url_input = gr.Textbox(label="🔗 Enter URL")
                with gr.Row():
                    enable_recursion = gr.Checkbox(
                        label="Enable Link Recursion",
                        value=False,
                        info="Extract data from linked pages within the same domain"
                    )
                    max_urls = gr.Slider(
                        minimum=1,
                        maximum=30,
                        value=2,
                        step=1,
                        label="Max URLs to Process",
                        visible=False,
                        info="Maximum number of URLs to process when recursion is enabled"
                    )
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
            inputs=[url_input, enable_recursion, max_urls],
            outputs=[process_output, train_preview, val_preview]
        ).then(
            fn=update_logs,
            outputs=[log_output]
        ).then(
            fn=get_source_info,
            outputs=[sources_display]
        )

        # Update max_urls visibility based on recursion checkbox
        enable_recursion.change(
            fn=lambda x: gr.update(visible=x),
            inputs=[enable_recursion],
            outputs=[max_urls]
        )

    return tab 