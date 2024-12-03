from typing import Dict, Any, List, Optional, Union
import gradio as gr
from core.handlers.discovery.discovery_mode_handler import DiscoveryModeHandler

class DiscoveryHandler:
    """Handler for Discovery Mode interactions"""
    
    def __init__(self, model_handler, rag_handler):
        self.model_handler = model_handler
        self.rag_handler = rag_handler
        self.discovery_handler = DiscoveryModeHandler(rag_handler)
        self.current_path = []
    
    async def handle_suggestion_click(
        self,
        suggestion: str,
        model_name: str,
        use_rag: bool = True
    ) -> Dict[str, Any]:
        """Handle suggestion chip click"""
        try:
            # Update navigation path
            self.current_path.append(suggestion)
            
            # Set the model
            self.model_handler.select_model(model_name)
            
            # Generate content
            content = await self.discovery_handler.generate_content(
                category_input=suggestion
            )
            
            # Generate follow-up suggestions
            followups = await self._generate_followups(suggestion, content)
            
            return {
                "content": content,
                "followups": followups,
                "path": self.current_path,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }
    
    async def _generate_followups(
        self,
        context: str,
        content: Dict[str, Any]
    ) -> List[str]:
        """Generate contextual follow-up suggestions"""
        try:
            # Use both RAG and AI to generate relevant follow-ups
            rag_context = await self.rag_handler.get_relevant_context(
                context,
                top_k=5
            ) if self.rag_handler else []
            
            # Extract topics from RAG context
            rag_topics = []
            for ctx in rag_context:
                metadata = ctx.get('metadata', {})
                if 'category' in metadata:
                    rag_topics.append(f"🔍 {metadata['category']}: {metadata.get('title', '')}")
            
            # Combine with AI-generated suggestions
            followups = content.get('suggestions', [])
            if rag_topics:
                followups.extend(rag_topics)
            
            # Deduplicate and limit
            return list(set(followups))[:8]
            
        except Exception as e:
            print(f"Error generating followups: {str(e)}")
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