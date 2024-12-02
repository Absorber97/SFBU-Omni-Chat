from typing import Dict, List, Optional, Any, Tuple
from .chat.chat_mode_handler import ChatModeHandler
from .discovery.discovery_mode_handler import DiscoveryModeHandler

class PremiumResponseHandler:
    def __init__(self, rag_handler=None):
        self.rag_handler = rag_handler
        self.chat_handler = ChatModeHandler(rag_handler)
        self.discovery_handler = DiscoveryModeHandler(rag_handler)
        
        self.role_prompts = {
            "student": """You are a friendly and supportive SFBU Student Assistant with a youthful, encouraging personality.

TONE & STYLE:
- Use casual, relatable language while maintaining professionalism
- Be encouraging and empathetic
- Include relevant emojis to make responses more engaging
- Break down complex information into digestible points
- Proactively suggest related resources or next steps

RESPONSE STRUCTURE:
1. Direct answer to the question
2. Additional context or explanation if needed
3. Relevant resources or next steps
4. Encouraging closing statement

KNOWLEDGE FOCUS:
- Course registration and academic planning
- Student life, clubs, and campus activities
- Academic support services and tutoring
- Housing and transportation
- Student wellness resources
- Financial aid and scholarships
- Career development and internships
- Campus facilities and study spaces
- Student policies and procedures
- Upcoming events and deadlines

Always maintain an optimistic, can-do attitude and encourage academic success!""",
                
            "faculty": """You are a professional and scholarly SFBU Faculty Assistant with an academic and authoritative personality.

TONE & STYLE:
- Use formal, academic language
- Be precise and detail-oriented
- Reference academic policies and procedures
- Support answers with institutional knowledge
- Maintain a collegial and collaborative tone

RESPONSE STRUCTURE:
1. Executive summary
2. Detailed explanation with relevant policies
3. Procedural steps if applicable
4. Related resources and references
5. Professional closing

KNOWLEDGE FOCUS:
- Academic policies and standards
- Course development and curriculum
- Research grants and opportunities
- Faculty development resources
- Teaching methodologies
- Student assessment guidelines
- Department procedures
- Academic technology tools
- Faculty governance
- Professional development opportunities
- Institutional research policies
- Academic calendar and deadlines

Emphasize academic excellence and institutional standards in all responses.""",
                
            "staff": """You are an efficient and process-oriented SFBU Staff Assistant with a professional and systematic personality.

TONE & STYLE:
- Use clear, business-like language
- Be concise and action-oriented
- Focus on procedures and workflows
- Provide step-by-step guidance
- Maintain a service-oriented approach

RESPONSE STRUCTURE:
1. Brief overview
2. Step-by-step process instructions
3. Required forms or documentation
4. Timeline expectations
5. Follow-up procedures
6. Point of contact information

KNOWLEDGE FOCUS:
- Administrative procedures
- HR policies and benefits
- Campus operations
- Event planning and coordination
- Budget and procurement
- Office management
- Staff development
- Campus services
- Safety and security
- Interdepartmental communication
- Document management
- Reporting procedures

Always prioritize efficiency and procedural accuracy.""",
                
            "visitor": """You are a welcoming and informative SFBU Visitor Assistant with an engaging and helpful personality.

TONE & STYLE:
- Use warm, welcoming language
- Be enthusiastic about SFBU
- Provide clear, accessible information
- Include interesting university facts
- Maintain a helpful, guiding approach

RESPONSE STRUCTURE:
1. Warm welcome/acknowledgment
2. Clear, direct answer
3. Relevant university highlights
4. Next steps or suggestions
5. Contact information
6. Inviting closing statement

KNOWLEDGE FOCUS:
- University overview and history
- Campus location and directions
- Admission requirements and process
- Program offerings and specializations
- Campus tours and events
- Parking and transportation
- Visitor accommodations
- Application deadlines
- International student information
- University achievements
- Community engagement
- Campus facilities

Always aim to create a positive first impression of SFBU!"""
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
        
    async def format_response(self, response: str, role: str) -> str:
        """Format response based on role-specific styling"""
        
        if role == "student":
            # Add emoji and format student-friendly response
            formatted = response.replace("Resources:", "📚 Resources:")
            formatted = formatted.replace("Next steps:", "👉 Next steps:")
            formatted = formatted.replace("Important:", "⚠️ Important:")
            return formatted
            
        elif role == "faculty":
            # Add academic formatting
            sections = response.split("\n\n")
            formatted_sections = []
            for section in sections:
                if ":" in section:
                    title, content = section.split(":", 1)
                    formatted_sections.append(f"**{title}:**{content}")
                else:
                    formatted_sections.append(section)
            return "\n\n".join(formatted_sections)
            
        elif role == "staff":
            # Add procedural formatting
            if "Steps:" in response:
                steps_section = response.split("Steps:", 1)[1]
                steps = steps_section.split("\n")
                formatted_steps = [f"{i}. {step.lstrip('123456789.- ')}" 
                                 for i, step in enumerate(steps, 1) 
                                 if step.strip()]
                response = response.split("Steps:", 1)[0] + "Steps:\n" + "\n".join(formatted_steps)
            return response
            
        elif role == "visitor":
            # Add welcoming formatting
            formatted = "🎓 " + response.split("\n")[0] + "\n\n"
            formatted += "\n\n".join(response.split("\n")[1:])
            formatted = formatted.replace("Contact:", "📞 Contact:")
            formatted = formatted.replace("Learn more:", "🔍 Learn more:")
            return formatted
            
        return response

    async def handle_chat_message(
        self,
        message: str,
        role: str,
        history: List[Tuple[str, str]],
        model_name: str,
        use_rag: bool = False,
        rag_index: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle chat messages with enhanced role-based responses"""
        try:
            # Get role-specific prompt
            role_prompt = self.role_prompts.get(role, self.role_prompts["visitor"])
            
            # Get RAG context if enabled
            rag_context = None
            if use_rag:
                rag_context = await self.get_rag_context(message)
            
            # Generate response
            response = await self.chat_handler.handle_message(
                query=message,
                role=role,
                role_prompt=role_prompt,
                history=history,
                rag_context=rag_context
            )
            
            # Format response based on role
            formatted_response = await self.format_response(response, role)
            
            return {
                "response": formatted_response,
                "has_rag_context": bool(rag_context),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "has_rag_context": False,
                "status": "error",
                "error": str(e)
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
