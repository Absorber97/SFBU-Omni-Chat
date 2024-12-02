from typing import Dict, Optional
from openai import AsyncOpenAI
from config import OPENAI_MODELS, ModelType, MODEL_PARAMS, OPENAI_API_KEY
import json

class DiscoveryModeHandler:
    def __init__(self, rag_handler=None):
        self.rag_handler = rag_handler
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
    async def generate_content(self, category: str, subcategory: str) -> Dict:
        try:
            # Get RAG context for the category
            rag_context = await self._get_rag_context(f"{category} {subcategory}")
            
            # Generate comprehensive content for discovery mode
            prompt = f"""Generate comprehensive information about {category} - {subcategory} at SFBU.
            Use this context when relevant: {rag_context}
            
            Include:
            1. A brief summary (2-3 sentences)
            2. Detailed explanation (2-3 paragraphs)
            3. Step-by-step guide if applicable (numbered steps)
            4. Common FAQs (3-5 questions)
            5. Related topics (3-5 suggestions)
            6. Follow-up questions (3-5 questions)
            
            Format the response as a JSON object with these keys:
            summary, detailed, steps, faq, suggestions, followups"""
            
            response = await self.client.chat.completions.create(
                model=OPENAI_MODELS[ModelType.CHAT.value],
                messages=[
                    {"role": "system", "content": "You are a knowledgeable SFBU assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=MODEL_PARAMS[ModelType.CHAT.value].get('temperature', 0.7),
                max_tokens=MODEL_PARAMS[ModelType.CHAT.value].get('max_tokens', 2000)
            )
            
            # Parse the response as JSON
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from API")
                
            return json.loads(content)
            
        except Exception as e:
            return {
                "summary": f"Error: {str(e)}",
                "detailed": "An error occurred",
                "steps": "",
                "faq": "",
                "suggestions": [],
                "followups": []
            }
            
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