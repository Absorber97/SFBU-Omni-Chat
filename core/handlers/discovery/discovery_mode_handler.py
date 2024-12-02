from typing import Dict, Optional
from openai import AsyncOpenAI
from config import OPENAI_MODELS, ModelType, MODEL_PARAMS, OPENAI_API_KEY
import json

class DiscoveryModeHandler:
    def __init__(self, rag_handler=None):
        self.rag_handler = rag_handler
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
    async def generate_content(self, category_input: str) -> Dict:
        """Generate comprehensive content for discovery mode"""
        try:
            # Parse category input
            category_parts = category_input.split(" - ", 1)
            if len(category_parts) != 2:
                raise ValueError("Invalid category format. Expected 'Category - Subcategory'")
                
            category, subcategory = category_parts
            
            # Extract context if provided
            context = ""
            if "Relevant Context:" in category_input:
                _, context_part = category_input.split("Relevant Context:", 1)
                context = context_part.strip()
            
            # Build context part of prompt
            context_section = ""
            if context:
                context_section = f"Using this context when relevant:\n{context}\n\n"
            
            # Generate comprehensive content
            prompt = (
                f"Generate comprehensive information about {category} - {subcategory} at SFBU.\n"
                f"{context_section}"
                "Include:\n"
                "1. A brief summary (2-3 sentences)\n"
                "2. Detailed explanation (2-3 paragraphs)\n"
                "3. Step-by-step guide if applicable (numbered steps)\n"
                "4. Common FAQs (3-5 questions)\n"
                "5. Related topics (3-5 suggestions)\n"
                "6. Follow-up questions (3-5 questions)\n\n"
                "Format the response as a JSON object with these keys:\n"
                "summary, detailed, steps, faq, suggestions, followups"
            )
            
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