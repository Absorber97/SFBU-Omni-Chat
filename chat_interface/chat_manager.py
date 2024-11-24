from typing import Dict, List, Any, Optional
from openai.types.chat import ChatCompletionMessageParam
from openai import OpenAI
from config import MODEL_CONFIG, MODEL_PARAMS, ModelType
from .chat_styling import ChatStyling

class ChatManager:
    def __init__(self, api_key: str):
        """Initialize chat manager with OpenAI client"""
        self.client = OpenAI(api_key=api_key)
        self.model_id = MODEL_CONFIG['base_name']
        self.styling = ChatStyling()
        self.conversation_history = []
        
    def set_model(self, model_id: str) -> None:
        """Set the model to use for chat"""
        self.model_id = model_id
        
    def moderate_content(self, text: str) -> Dict:
        """Check content using OpenAI moderation"""
        try:
            response = self.client.moderations.create(input=text)
            result = response.results[0]
            
            if result.flagged:
                # Get the specific flags that were triggered
                flags = {k: v for k, v in result.categories.dict().items() if v}
                return {
                    'flagged': True,
                    'flags': flags,
                    'message': "Content flagged for moderation"
                }
            return {'flagged': False}
            
        except Exception as e:
            raise Exception(f"Moderation error: {str(e)}")
        
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using the selected model"""
        try:
            # Convert messages to ChatCompletionMessageParam format
            formatted_messages: List[ChatCompletionMessageParam] = [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in messages
            ]
            
            # Add system prompt at the beginning
            system_message: ChatCompletionMessageParam = {
                "role": "system",
                "content": self.styling.get_system_prompt()
            }
            formatted_messages.insert(0, system_message)
            
            # Get model parameters with proper type checking
            params = MODEL_PARAMS[ModelType.CHAT.value]
            temperature = params.get('temperature', 0.7)  # Default if not found
            max_tokens = params.get('max_tokens', 1500)  # Default if not found
            
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise Exception("Received empty response from API")
                
            return content
            
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Return conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = [] 