from typing import Dict, Optional
from openai import AsyncOpenAI
from config import OPENAI_MODELS, ModelType, MODEL_PARAMS, OPENAI_API_KEY
import json
import logging

logger = logging.getLogger(__name__)

class DiscoveryModeHandler:
    def __init__(self, rag_handler=None):
        self.rag_handler = rag_handler
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        logger.info("Initialized DiscoveryModeHandler")
        
    async def generate_content(
        self,
        category_input: str,
        model_name: str,
        use_rag: bool = True
    ) -> Dict:
        """Generate comprehensive content for discovery mode"""
        try:
            logger.info(f"Generating content for: {category_input}")
            logger.info(f"Using model: {model_name}, RAG enabled: {use_rag}")
            
            # Get RAG context if enabled
            rag_context = ""
            if use_rag:
                try:
                    rag_context = await self._get_rag_context(category_input)
                    if rag_context:
                        logger.info("Successfully retrieved RAG context")
                    else:
                        logger.warning("No RAG context found")
                except Exception as e:
                    logger.error(f"Error getting RAG context: {str(e)}")
            
            # Build context-aware prompt
            context_section = f"Using this relevant context:\n{rag_context}\n\n" if rag_context else ""
            
            # Generate comprehensive content
            prompt = (
                f"Generate comprehensive, engaging information about {category_input} at SFBU.\n"
                f"{context_section}"
                "Structure the response with these sections:\n\n"
                "1. SUMMARY (2-3 engaging sentences)\n"
                "- Brief, compelling overview\n"
                "- Key highlights or unique aspects\n"
                "- Why this matters to students\n\n"
                "2. DETAILED EXPLANATION (2-3 well-structured paragraphs)\n"
                "- Comprehensive coverage with specific examples\n"
                "- Current state and future developments\n"
                "- Real-world applications or benefits\n\n"
                "3. KEY POINTS (4-6 bullet points)\n"
                "- Essential takeaways\n"
                "- Important facts or features\n"
                "- Unique advantages\n\n"
                "4. STEP-BY-STEP GUIDE (if applicable)\n"
                "- Clear, actionable steps\n"
                "- Prerequisites or requirements\n"
                "- Expected outcomes\n\n"
                "5. FAQ SECTION (3-5 insightful Q&A pairs)\n"
                "- Common questions with detailed answers\n"
                "- Address potential concerns\n"
                "- Include practical examples\n\n"
                "6. RELATED TOPICS (3-5 engaging suggestions)\n"
                "- Connected areas of interest\n"
                "- Start each with an emoji\n"
                "- Make them descriptive and interesting\n\n"
                "7. FOLLOW-UP QUESTIONS (3-5 thought-provoking questions)\n"
                "- Questions for deeper exploration\n"
                "- Start each with an emoji\n"
                "- Make them engaging and specific\n\n"
                "Format the response as a JSON object with these keys:\n"
                "summary, detailed, bullets, steps, faq (as {question: answer}), suggestions, followups"
            )
            
            logger.info("Sending request to OpenAI")
            response = await self.client.chat.completions.create(
                model=model_name,  # Use selected model
                messages=[
                    {"role": "system", "content": "You are a knowledgeable SFBU assistant, skilled at providing comprehensive, engaging information with a focus on student relevance and practical value."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={ "type": "json_object" }  # Ensure JSON response
            )
            logger.info("Received response from OpenAI")
            
            # Parse and enhance the response
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from API")
            
            try:
                result = json.loads(content)
                logger.info("Successfully parsed JSON response")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {str(e)}")
                raise ValueError(f"Invalid JSON response: {str(e)}")
            
            # Add bullet points if not present
            if "bullets" in result:
                # Convert to list if it's a string
                if isinstance(result["bullets"], str):
                    bullet_points = result["bullets"].split("\n")
                else:
                    bullet_points = result["bullets"]
                
                # Add bullet points if not present
                result["bullets"] = "\n".join([
                    f"• {point.strip()}" if not point.strip().startswith(("•", "- ", "* ", "→ ", "▶ ", "◆ "))
                    else point.strip()
                    for point in bullet_points
                    if point.strip()  # Skip empty lines
                ])
                logger.info("Enhanced bullet points")
            
            # Ensure all fields are present and properly formatted for Gradio
            result = {
                "summary": str(result.get("summary", "")),
                "detailed": str(result.get("detailed", "")),
                "bullets": str(result.get("bullets", "")),
                "steps": str(result.get("steps", "")),
                "faq": self._format_faq(result.get("faq", {})),
                "suggestions": self._format_list(result.get("suggestions", [])),
                "followups": self._format_list(result.get("followups", []))
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}", exc_info=True)
            return {
                "summary": f"Error: {str(e)}",
                "detailed": "An error occurred",
                "bullets": "",
                "steps": "",
                "faq": "",
                "suggestions": "",
                "followups": ""
            }
    
    def _format_faq(self, faq_dict: dict) -> str:
        """Format FAQ dictionary into a readable string"""
        if not faq_dict:
            return ""
        
        formatted_faqs = []
        for q, a in faq_dict.items():
            formatted_faqs.append(f"Q: {q}\nA: {a}")
        
        return "\n\n".join(formatted_faqs)
    
    def _format_list(self, items: list) -> str:
        """Format a list into a string with line breaks"""
        if not items:
            return ""
        
        return "\n".join(str(item) for item in items)
    
    async def _get_rag_context(self, query: str) -> str:
        """Get relevant context from RAG system"""
        if not self.rag_handler:
            logger.warning("No RAG handler available")
            return ""
            
        try:
            logger.info(f"Getting RAG context for query: {query}")
            docs = await self.rag_handler.get_relevant_docs(query)
            if not docs:
                logger.warning("No relevant documents found")
                return ""
                
            context = "\n".join([doc.text for doc in docs])
            logger.info(f"Retrieved {len(docs)} relevant documents")
            return context
            
        except Exception as e:
            logger.error(f"Error getting RAG context: {str(e)}", exc_info=True)
            return "" 