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
        history: Optional[List] = None
    ) -> str:
        try:
            # Get RAG context if available
            rag_context = await self._get_rag_context(query)
            
            # Combine history for context
            chat_history = self._format_history(history) if history else []
            
            # Construct the full prompt
            system_prompt = f"{role_prompt}\n\nUse this additional context when relevant: {rag_context}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                *chat_history,
                {"role": "user", "content": query}
            ]
            
            # Use OpenAI API to generate response
            response = await self.client.chat.completions.create(
                model=OPENAI_MODELS[ModelType.CHAT.value],
                messages=messages,
                temperature=MODEL_PARAMS[ModelType.CHAT.value].get('temperature', 0.7),
                max_tokens=MODEL_PARAMS[ModelType.CHAT.value].get('max_tokens', 1000)
            )
            
            return response.choices[0].message.content or "I apologize, but I couldn't generate a response."
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
            
    async def _get_rag_context(self, query: str) -> str:
        """Get relevant context from RAG system"""
        if not self.rag_handler:
            return ""
            
        try:
            docs = await self.rag_handler.get_relevant_docs(query)
            context = "\n".join([doc.page_content for doc in docs])
            return context if context else ""
            
        except Exception as e:
            print(f"RAG error: {str(e)}")
            return ""
            
    def _format_history(self, history: List) -> List[Dict[str, str]]:
        """Format chat history for the API"""
        formatted_history = []
        for user_msg, assistant_msg in history:
            formatted_history.extend([
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": assistant_msg}
            ])
        return formatted_history 