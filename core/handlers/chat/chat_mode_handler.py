from typing import Dict, List, Optional, Union
from openai import AsyncOpenAI
from config import OPENAI_MODELS, ModelType, MODEL_PARAMS, OPENAI_API_KEY
import logging

logger = logging.getLogger(__name__)

class ChatModeHandler:
    def __init__(self, rag_handler=None):
        self.rag_handler = rag_handler
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        logger.info("Initialized ChatModeHandler")
        
    def _get_role_structure(self, role: str) -> str:
        """Get role-specific response structure"""
        if role in ["faculty", "staff"]:
            return """RESPONSE STRUCTURE:
1. Professional Opening:
   - Formal greeting
   - Clear acknowledgment of the query

2. Comprehensive Answer (2-3 paragraphs):
   - Detailed analysis
   - Reference to SFBU policies
   - Supporting data or research

3. Implementation/Resources:
   - Relevant procedures
   - Available resources
   - Contact information

4. Professional Closing:
   - Next steps
   - Additional considerations
   - Follow-up availability

FORMAT REQUIREMENTS:
- Use descriptive headers (##)
- Bullet points for lists
- Bold (**) key terms
- 1-2 relevant emojis
- Clear section breaks
- Tables for complex data
- Citations where applicable"""
        else:  # student or visitor
            return """RESPONSE STRUCTURE:
1. Friendly Opening:
   - Warm greeting with emoji
   - Show enthusiasm

2. Clear Answer:
   - Simple, direct explanation
   - Relatable examples
   - Practical tips

3. Helpful Resources:
   - Key contacts
   - Where to learn more
   - Quick tips

4. Engaging Closing:
   - Encouragement
   - Next steps
   - Open invitation for questions

FORMAT REQUIREMENTS:
- Conversational tone
- Short, clear paragraphs
- 3-4 engaging emojis
- Simple bullet points
- Friendly examples"""

    async def handle_message(
        self,
        query: str,
        role: str,
        role_prompt: str,
        history: Optional[List] = None,
        rag_context: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> str:
        """Handle chat messages with role-specific context"""
        try:
            logger.info(f"Handling message for role: {role}, model: {model_name}")
            
            # Format chat history
            chat_history = self._format_history(history) if history else []
            
            # Get role-specific structure and traits
            response_structure = self._get_role_structure(role)
            personality_traits = self._get_role_traits(role)
            
            # Build role-specific system prompt
            system_prompt = f"""You are an SFBU AI Assistant with the following traits:
{personality_traits}

{response_structure}

RESPONSE LENGTH:
{self._get_length_guide(role)}

TONE GUIDELINES:
- Maintain consistent {role}-appropriate voice
- Use {self._get_language_style(role)}
- Include {self._get_example_style(role)}"""

            # Add RAG context if available
            if rag_context:
                system_prompt = f"{system_prompt}\n\nRelevant Context:\n{rag_context}\n\nNaturally integrate this context while maintaining your role's style."
            
            # Construct messages array
            messages = [
                {"role": "system", "content": system_prompt},
                *chat_history,
                {"role": "user", "content": query}
            ]
            
            # Generate response with role-appropriate parameters
            response = await self.client.chat.completions.create(
                model=model_name or OPENAI_MODELS[ModelType.CHAT.value],
                messages=messages,
                temperature=self._get_temperature(role),
                max_tokens=self._get_max_tokens(role),
                presence_penalty=0.6,
                frequency_penalty=0.3
            )
            
            content = response.choices[0].message.content
            if not content:
                logger.warning("Empty response from API")
                return "I apologize, but I couldn't generate a response."
                
            logger.info("Successfully generated response")
            return content
            
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}", exc_info=True)
            return f"I apologize, but I encountered an error: {str(e)}"

    def _get_length_guide(self, role: str) -> str:
        """Get role-specific length guidelines"""
        if role == "faculty":
            return "Provide comprehensive responses (4-5 paragraphs) with detailed analysis and academic context"
        elif role == "staff":
            return "Give thorough responses (3-4 paragraphs) focusing on procedures and practical implementation"
        elif role == "student":
            return "Keep responses concise and engaging (2-3 short paragraphs) with clear action items"
        else:  # visitor
            return "Provide brief, welcoming responses (2 paragraphs) highlighting key information"

    def _get_language_style(self, role: str) -> str:
        """Get role-specific language style"""
        styles = {
            "faculty": "formal academic language with field-specific terminology",
            "staff": "professional administrative language with procedural clarity",
            "student": "friendly, relatable language with current student terms",
            "visitor": "welcoming, accessible language with clear explanations"
        }
        return styles.get(role, styles["visitor"])

    def _get_example_style(self, role: str) -> str:
        """Get role-specific example style"""
        styles = {
            "faculty": "academic scenarios and research-based examples",
            "staff": "specific procedural examples and administrative cases",
            "student": "relatable student experiences and practical scenarios",
            "visitor": "general university examples and visitor-relevant situations"
        }
        return styles.get(role, styles["visitor"])

    def _get_temperature(self, role: str) -> float:
        """Get role-specific temperature setting"""
        temps = {
            "faculty": 0.6,  # More focused on accuracy
            "staff": 0.65,   # Balance of accuracy and flexibility
            "student": 0.75, # More conversational
            "visitor": 0.7   # Welcoming but informative
        }
        return temps.get(role, 0.7)

    def _get_max_tokens(self, role: str) -> int:
        """Get role-specific max tokens"""
        tokens = {
            "faculty": 2500,  # Longer, comprehensive responses
            "staff": 2000,    # Detailed but focused responses
            "student": 1000,  # Shorter, concise responses
            "visitor": 800    # Brief, welcoming responses
        }
        return tokens.get(role, 1000)

    def _format_history(self, history: List[List[str]]) -> List[Dict[str, str]]:
        """Format chat history for the API"""
        if not history:
            return []
            
        formatted_history = []
        for user_msg, assistant_msg in history:
            formatted_history.extend([
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": assistant_msg}
            ])
        return formatted_history 

    def _get_role_traits(self, role: str) -> str:
        """Get personality traits for specific roles"""
        traits = {
            "student": """- Use friendly, relatable language
- Show enthusiasm for learning and campus life
- Share personal-feeling examples
- Be encouraging and supportive
- Use current student terminology
- Express understanding of student challenges""",
            
            "faculty": """- Maintain scholarly tone
- Emphasize academic excellence
- Reference research and pedagogy
- Show deep subject expertise
- Focus on educational impact
- Use professional academic language""",
            
            "staff": """- Project efficiency and organization
- Focus on processes and procedures
- Maintain service-oriented approach
- Show attention to detail
- Reference specific SFBU systems
- Use clear administrative language""",
            
            "visitor": """- Be welcoming and informative
- Show enthusiasm about SFBU
- Highlight unique campus features
- Use accessible language
- Share engaging university facts
- Maintain helpful, guiding tone"""
        }
        return traits.get(role, traits["visitor"])