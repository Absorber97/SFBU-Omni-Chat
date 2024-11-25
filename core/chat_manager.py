from typing import List, Dict, Any
from openai import OpenAI
import logging

class ChatManager:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model_id = None
        self.logger = logging.getLogger(__name__)

    def set_model(self, model_id: str) -> Dict[str, Any]:
        """Set the model to use for chat"""
        try:
            if not model_id:
                raise ValueError("Model ID cannot be empty")
            self.model_id = model_id
            self.logger.info(f"Chat model set to: {model_id}")
            return {"status": "success", "message": f"Model set to: {model_id}"}
        except Exception as e:
            self.logger.error(f"Error setting model: {str(e)}")
            return {"status": "error", "message": str(e)}

    def generate_response(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Generate a response using the specified model"""
        try:
            if not self.model_id:
                raise ValueError("No model selected. Please select a model first.")

            if not messages:
                raise ValueError("No messages provided for response generation")

            # Log the request for debugging
            self.logger.debug(f"Generating response with model {self.model_id}")
            self.logger.debug(f"Messages: {messages}")
            self.logger.debug(f"Temperature: {temperature}")

            # Make the API call
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=temperature
            )

            # Validate response
            if not response or not response.choices:
                raise ValueError("Received invalid response from API")

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Received empty response from API")

            return content

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg) 