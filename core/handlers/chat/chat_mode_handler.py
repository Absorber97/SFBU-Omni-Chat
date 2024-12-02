from typing import Dict, List, Optional
from openai import AsyncOpenAI
from config import OPENAI_MODELS, ModelType, MODEL_PARAMS, OPENAI_API_KEY

class ChatModeHandler:
    def __init__(self, rag_handler=None):
        self.rag_handler = rag_handler
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
    async def handle_message(
        self,
        query: str,
        role: str,
        role_prompt: str,
        history: Optional[List] = None,
        rag_context: Optional[str] = None
    ) -> str:
        """Handle chat messages with role-specific context"""
        try:
            # Format chat history
            chat_history = self._format_history(history) if history else []
            
            # Combine role prompt with RAG context if available
            system_prompt = role_prompt
            if rag_context:
                system_prompt = f"{role_prompt}\n\nRelevant Context:\n{rag_context}"
            
            # Construct messages array
            messages = [
                {"role": "system", "content": system_prompt},
                *chat_history,
                {"role": "user", "content": query}
            ]
            
            # Generate response
            response = await self.client.chat.completions.create(
                model=OPENAI_MODELS[ModelType.CHAT.value],
                messages=messages,
                temperature=MODEL_PARAMS[ModelType.CHAT.value].get('temperature', 0.7),
                max_tokens=MODEL_PARAMS[ModelType.CHAT.value].get('max_tokens', 1000)
            )
            
            return response.choices[0].message.content or "I apologize, but I couldn't generate a response."
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
            
    def _format_history(self, history: List[List[str]]) -> List[Dict[str, str]]:
        """Format chat history for the API"""
        if not history:
            return []
            
        formatted_history = []
        for user_msg, assistant_msg in history:
            formatted_history.extend([
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": assistant_msg}
            ])
        return formatted_history 