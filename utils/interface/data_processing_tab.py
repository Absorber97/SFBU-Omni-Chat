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
                with gr.Row():
                    pdf_input = gr.File(
                        label="📒 Upload PDF(s)",
                        file_count="multiple",  # Allow multiple files
                        file_types=[".pdf"]
                    )
                    enable_batch_pdf = gr.Checkbox(
                        label="Enable Batch PDF Processing",
                        value=False,
                        info="Process multiple PDFs at once"
                    )
                process_pdf_btn = gr.Button("📥 Process PDF(s)")
                url_input = gr.Textbox(
                    label="🔗 Enter URL(s)",
                    placeholder="Enter single URL or multiple URLs (one per line)",
                    lines=3
                )
                with gr.Row():
                    enable_recursion = gr.Checkbox(
                        label="Enable Link Recursion",
                        value=False,
                        info="Extract data from linked pages within the same domain"
                    )
                    enable_batch = gr.Checkbox(
                        label="Enable Batch Processing",
                        value=False,
                        info="Process multiple URLs (one per line)"
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
                process_url_btn = gr.Button("🌐 Process URL(s)")
        
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
            inputs=[pdf_input, enable_batch_pdf],
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
            inputs=[url_input, enable_recursion, enable_batch, max_urls],
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

        # Update URL input appearance based on batch processing
        enable_batch.change(
            fn=lambda x: gr.update(lines=5 if x else 3),
            inputs=[enable_batch],
            outputs=[url_input]
        )

    return tab 