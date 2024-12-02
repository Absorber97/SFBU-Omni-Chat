from typing import Dict, List, Optional
from .chat.chat_mode_handler import ChatModeHandler
from .discovery.discovery_mode_handler import DiscoveryModeHandler

class PremiumResponseHandler:
    def __init__(self, rag_handler=None):
        self.chat_handler = ChatModeHandler(rag_handler)
        self.discovery_handler = DiscoveryModeHandler(rag_handler)
        
        self.role_prompts = {
            "student": """You are assisting a student at SFBU. Focus on:
                - Academic guidance and course selection
                - Student life and campus activities
                - Resources and support services
                - Housing and facilities
                - Career development opportunities
                Tone: Friendly, supportive, and encouraging""",
                
            "faculty": """You are assisting SFBU faculty. Focus on:
                - Teaching resources and tools
                - Research opportunities and grants
                - Administrative procedures
                - Student assessment guidelines
                - Department policies
                Tone: Professional and collaborative""",
                
            "staff": """You are assisting SFBU staff. Focus on:
                - Administrative procedures
                - Operational policies
                - Staff resources and tools
                - Campus services and facilities
                - Event coordination
                Tone: Efficient and process-oriented""",
                
            "visitor": """You are assisting a visitor to SFBU. Focus on:
                - General university information
                - Admissions process
                - Campus tours and visits
                - Program offerings
                - Contact information
                Tone: Welcoming and informative"""
        }
        
    async def generate_chat_response(
        self,
        query: str,
        role: str,
        history: Optional[List] = None
    ) -> str:
        role_prompt = self.role_prompts.get(role, self.role_prompts["visitor"])
        return await self.chat_handler.handle_message(query, role, role_prompt, history)
        
    async def generate_discovery_content(self, category: str) -> Dict:
        category_parts = category.split(" - ", 1)
        if len(category_parts) != 2:
            return {
                "summary": "Invalid category format",
                "detailed": "Please provide both category and subcategory",
                "steps": "",
                "faq": "",
                "suggestions": [],
                "followups": []
            }
            
        main_category, subcategory = category_parts
        return await self.discovery_handler.generate_content(main_category, subcategory)
