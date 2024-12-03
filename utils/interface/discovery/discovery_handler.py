from typing import Dict, Any, List, Optional, Union
import gradio as gr
import logging
from core.handlers.discovery.discovery_mode_handler import DiscoveryModeHandler

logger = logging.getLogger(__name__)

class DiscoveryHandler:
    """Handler for Discovery Mode interactions"""
    
    def __init__(self, model_handler, rag_handler):
        self.model_handler = model_handler
        self.rag_handler = rag_handler
        self.discovery_handler = DiscoveryModeHandler(rag_handler)
        self.current_path = []
        logger.info("Initialized DiscoveryHandler")
    
    async def handle_suggestion_click(
        self,
        suggestion: str,
        model_name: str,
        use_rag: bool,
        rag_index: str
    ) -> List[Any]:
        """Handle suggestion chip click"""
        try:
            logger.info(f"Processing suggestion: {suggestion}")
            logger.info(f"Using model: {model_name}, RAG enabled: {use_rag}, RAG index: {rag_index}")
            
            # Update navigation path
            self.current_path.append(suggestion)
            
            # Set the model
            self.model_handler.select_model(model_name)
            logger.info(f"Selected model: {model_name}")
            
            # Set RAG index if using RAG
            if use_rag and rag_index:
                try:
                    self.rag_handler._load_index(rag_index)
                    logger.info(f"Loaded RAG index: {rag_index}")
                except Exception as e:
                    logger.error(f"Error loading RAG index: {str(e)}")
                    use_rag = False
            
            # Generate content
            content = await self.discovery_handler.generate_content(
                category_input=suggestion,
                model_name=model_name,
                use_rag=use_rag
            )
            logger.info("Generated content successfully")
            
            # Generate follow-up suggestions
            followups = await self._generate_followups(suggestion, content)
            logger.info(f"Generated {len(followups)} followup suggestions")
            
            # Return all required outputs in correct order
            return [
                content.get("summary", ""),
                content.get("detailed", ""),
                content.get("bullets", ""),
                content.get("steps", ""),
                content.get("faq", ""),
                gr.update(value="\n".join(content.get("suggestions", []))),
                gr.update(value="\n".join(followups)),
                " → ".join(self.current_path)
            ]
            
        except Exception as e:
            logger.error(f"Error handling suggestion click: {str(e)}", exc_info=True)
            error_msg = f"Error: {str(e)}"
            return [
                error_msg,
                "An error occurred",
                "",
                "",
                "",
                gr.update(value=""),
                gr.update(value=""),
                " → ".join(self.current_path)
            ]
    
    async def _generate_followups(
        self,
        context: str,
        content: Dict[str, Any]
    ) -> List[str]:
        """Generate contextual follow-up suggestions"""
        try:
            logger.info("Generating followup suggestions")
            
            # Use both RAG and AI to generate relevant follow-ups
            rag_context = []
            if self.rag_handler:
                try:
                    # Try get_relevant_context first
                    logger.info("Attempting to get RAG context")
                    rag_context = await self.rag_handler.get_relevant_context(
                        query=context,
                        top_k=5
                    )
                    logger.info("Successfully retrieved RAG context")
                except AttributeError:
                    logger.warning("get_relevant_context not found, trying get_relevant_docs")
                    try:
                        # Fallback to get_relevant_docs
                        docs = await self.rag_handler.get_relevant_docs(context)
                        rag_context = [
                            {"metadata": getattr(doc, "metadata", {}), "content": getattr(doc, "text", "")}
                            for doc in docs
                        ]
                        logger.info("Successfully retrieved RAG docs")
                    except Exception as e:
                        logger.error(f"Error getting RAG docs: {str(e)}")
                        rag_context = []
            
            # Extract topics from RAG context
            rag_topics = []
            for ctx in rag_context:
                try:
                    if isinstance(ctx, dict):
                        metadata = ctx.get('metadata', {})
                    else:
                        metadata = getattr(ctx, 'metadata', {})
                    
                    if metadata and 'category' in metadata:
                        topic = f"🔍 {metadata['category']}: {metadata.get('title', '')}"
                        rag_topics.append(topic)
                        logger.debug(f"Added RAG topic: {topic}")
                except Exception as e:
                    logger.error(f"Error processing RAG context item: {str(e)}")
            
            # Get AI-generated suggestions and convert to list if needed
            ai_suggestions = content.get('suggestions', [])
            if isinstance(ai_suggestions, str):
                ai_suggestions = [s.strip() for s in ai_suggestions.split('\n') if s.strip()]
            
            # Combine with RAG topics
            followups = list(ai_suggestions)  # Create new list
            if rag_topics:
                followups.extend(rag_topics)
                logger.info(f"Combined {len(rag_topics)} RAG topics with {len(ai_suggestions)} AI suggestions")
            
            # Deduplicate and limit
            unique_followups = list(set(followups))[:8]
            logger.info(f"Generated {len(unique_followups)} unique followup suggestions")
            return unique_followups
            
        except Exception as e:
            logger.error(f"Error generating followups: {str(e)}", exc_info=True)
            return []
    
    def update_display(
        self,
        content: Dict[str, Any],
        components: Dict[str, Union[gr.Markdown, gr.Button, gr.Row, gr.Column]]
    ) -> Dict[str, Dict[str, Any]]:
        """Update display components with new content"""
        try:
            return {
                "summary": gr.update(value=content.get("summary", "")),
                "details": gr.update(value=content.get("detailed", "")),
                "bullets": gr.update(value=content.get("bullets", "")),
                "steps": gr.update(value=content.get("steps", "")),
                "faq": gr.update(value=content.get("faq", "")),
                "path": gr.update(value=" → ".join(self.current_path)),
                "related": gr.update(value="\n".join(content.get("suggestions", []))),
                "followups": gr.update(value="\n".join(content.get("followups", [])))
            }
        except Exception as e:
            print(f"Error updating display: {str(e)}")
            return {} 