from typing import Dict, Any, List
from openai import OpenAI
from config import OPENAI_MODELS, MODEL_PARAMS

class ChatManager:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.conversation_history: List[Dict[str, str]] = []
        
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate single chat response using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODELS['chat'],
                messages=messages,
                **MODEL_PARAMS['chat']
            )
            
            # Get response content
            message_content = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": message_content
            })
            
            return message_content
            
        except Exception as e:
            self.logger.error(f"Error generating chat response: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Return conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = [] 