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
            
            # Create button updates with actual suggestions
            button_updates = []
            for i in range(8):
                if i < len(followups):
                    button_updates.append(gr.update(
                        value=followups[i],
                        visible=True
                    ))
                else:
                    button_updates.append(gr.update(
                        value="",
                        visible=False
                    ))
            
            # Return all required outputs in correct order
            return [
                content.get("summary", ""),        # Summary markdown
                content.get("detailed", ""),       # Details markdown
                content.get("bullets", ""),        # Bullets markdown
                content.get("steps", ""),          # Steps markdown
                content.get("faq", ""),            # FAQ markdown
                *button_updates,                   # 8 suggestion buttons
                " → ".join(self.current_path)      # Path markdown
            ]
            
        except Exception as e:
            logger.error(f"Error handling suggestion click: {str(e)}", exc_info=True)
            error_msg = f"Error: {str(e)}"
            # Return error state for all components
            return [
                error_msg,                  # Summary markdown
                "An error occurred",        # Details markdown
                "",                         # Bullets markdown
                "",                         # Steps markdown
                "",                         # FAQ markdown
                *[gr.update(value="", visible=False) for _ in range(8)],  # 8 buttons
                " → ".join(self.current_path)  # Path markdown
            ]
    
    async def _generate_followups(
        self,
        context: str,
        content: Dict[str, Any]
    ) -> List[str]:
        """Generate contextual follow-up suggestions"""
        try:
            logger.info("Generating followup suggestions")
            
            # Get AI-generated suggestions and convert to list if needed
            ai_suggestions = content.get('suggestions', [])
            if isinstance(ai_suggestions, str):
                ai_suggestions = [s.strip() for s in ai_suggestions.split('\n') if s.strip()]
            
            # Clean and format suggestions
            formatted_suggestions = []
            emojis = ['📚', '🎓', '💡', '🔬', '📝', '🌟', '💼', '🤝']
            emoji_index = 0
            
            for suggestion in ai_suggestions:
                # Remove any existing emojis
                cleaned_suggestion = ' '.join([
                    word for word in suggestion.split()
                    if not any(char in word for char in ['📚', '🎓', '💡', '🔬', '📝', '🌟', '💼', '🤝', '🔍'])
                ]).strip()
                
                # Skip if suggestion is too short or incomplete
                if len(cleaned_suggestion) < 10 or not cleaned_suggestion.endswith(('.', '?')):
                    continue
                    
                # Add single emoji and format
                formatted_suggestion = f"{emojis[emoji_index % len(emojis)]} {cleaned_suggestion}"
                formatted_suggestions.append(formatted_suggestion)
                emoji_index += 1
            
            # Add RAG-based suggestions if available
            if self.rag_handler:
                try:
                    rag_context = await self.rag_handler.get_relevant_context(
                        query=context,
                        top_k=3  # Limit RAG suggestions
                    )
                    
                    for ctx in rag_context:
                        if isinstance(ctx, dict):
                            title = ctx.get('metadata', {}).get('title', '')
                            if title and len(title) > 10:
                                formatted_suggestions.append(f"🔍 {title}")
                except Exception as e:
                    logger.error(f"Error processing RAG suggestions: {str(e)}")
            
            # Deduplicate, limit, and ensure complete sentences
            unique_suggestions = []
            seen = set()
            for suggestion in formatted_suggestions:
                clean_text = suggestion[2:].lower()  # Remove emoji and lowercase for comparison
                if clean_text not in seen and len(unique_suggestions) < 8:
                    seen.add(clean_text)
                    unique_suggestions.append(suggestion)
            
            logger.info(f"Generated {len(unique_suggestions)} unique followup suggestions")
            return unique_suggestions
            
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