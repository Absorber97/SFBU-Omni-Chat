from typing import Dict, Any, List
from openai import OpenAI

class ChatManager:
    def __init__(self, model_id: str, api_key: str):
        self.model_id = model_id
        self.client = OpenAI(api_key=api_key)
        self.conversation_history = []
        
    def generate_response(self, user_input: str) -> Dict[str, Any]:
        """
        Generate response using the fine-tuned model
        """
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Add system message for personality
            system_message = {
                "role": "system",
                "content": "You are SFBU Omni Chat 🎓, a friendly and knowledgeable AI assistant for San Francisco Bay University. "
                          "You're enthusiastic about helping students and always maintain a positive, supportive tone. "
                          "You use occasional emojis to make conversations engaging but keep them professional. "
                          "If you're not sure about something, you'll honestly say so and suggest contacting SFBU staff."
            }
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[system_message] + self.conversation_history,
                temperature=0.7,
                max_tokens=150
            )
            
            # Add assistant response to history
            assistant_response = response.choices[0].message.content
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_response
            })
            
            return {
                'status': 'success',
                'response': assistant_response
            }
            
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