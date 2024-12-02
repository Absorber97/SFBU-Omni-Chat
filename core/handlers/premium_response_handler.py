from typing import Dict, List, Optional, Any
from .chat.chat_mode_handler import ChatModeHandler
from .discovery.discovery_mode_handler import DiscoveryModeHandler

class PremiumResponseHandler:
    def __init__(self, rag_handler=None):
        self.rag_handler = rag_handler
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
        
    async def get_rag_context(self, query: str) -> Optional[str]:
        """Get relevant context from RAG system"""
        if not self.rag_handler:
            return None
            
        try:
            # Get relevant documents
            contexts = self.rag_handler.get_relevant_context(query, top_k=3)
            
            if not contexts:
                return None
                
            # Format contexts with confidence scores
            formatted_contexts = []
            for ctx in contexts:
                confidence = ctx.get('score', 0.0)
                question = ctx.get('metadata', {}).get('question', '')
                answer = ctx.get('metadata', {}).get('answer', '')
                
                if question and answer:
                    formatted_contexts.append(
                        f"[Confidence: {confidence:.2f}]\n"
                        f"Q: {question}\n"
                        f"A: {answer}"
                    )
            
            if formatted_contexts:
                return "Relevant Information:\n" + "\n\n".join(formatted_contexts)
            return None
            
        except Exception as e:
            print(f"RAG context retrieval failed: {str(e)}")
            return None
        
    async def generate_chat_response(
        self,
        query: str,
        role: str,
        history: Optional[List] = None,
        use_rag: bool = True
    ) -> Dict[str, Any]:
        """Generate chat response with role-specific context and RAG integration"""
        try:
            # Get role-specific prompt
            role_prompt = self.role_prompts.get(role, self.role_prompts["visitor"])
            
            # Get RAG context if enabled
            rag_context = None
            if use_rag:
                rag_context = await self.get_rag_context(query)
            
            # Combine role prompt with RAG context if available
            system_prompt = role_prompt
            if rag_context:
                system_prompt = f"{role_prompt}\n\n{rag_context}"
            
            # Generate response using chat handler
            response = await self.chat_handler.handle_message(
                query=query,
                role=role,
                role_prompt=system_prompt,
                history=history
            )
            
            return {
                "response": response,
                "has_rag_context": bool(rag_context),
                "status": "success"
            }
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "has_rag_context": False,
                "status": "error",
                "error": error_msg
            }
        
    async def generate_discovery_content(
        self,
        category: str,
        use_rag: bool = True
    ) -> Dict[str, Any]:
        """Generate discovery content with RAG integration"""
        try:
            # Get RAG context if enabled
            rag_context = None
            if use_rag:
                rag_context = await self.get_rag_context(category)
            
            # Add context to category if available
            category_with_context = category
            if rag_context:
                category_with_context = f"{category}\n\n{rag_context}"
            
            # Generate content using discovery handler
            content = await self.discovery_handler.generate_content(category_with_context)
            
            return {
                **content,
                "has_rag_context": bool(rag_context),
                "status": "success"
            }
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            return {
                "summary": error_msg,
                "detailed": "An error occurred",
                "steps": "",
                "faq": "",
                "suggestions": [],
                "followups": [],
                "has_rag_context": False,
                "status": "error",
                "error": error_msg
            }
