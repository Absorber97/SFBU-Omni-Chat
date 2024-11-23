from typing import Dict, Any, List
from openai import OpenAI
from config import OPENAI_MODELS, MODEL_PARAMS

class ChatManager:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate chat response using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODELS['chat'],
                messages=messages,
                **MODEL_PARAMS['chat']
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Return conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = [] 