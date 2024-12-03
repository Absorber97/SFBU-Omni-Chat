from typing import Dict, Any, List, Optional, Union
import gradio as gr
import logging
import asyncio
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get OpenAI API key from environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found in environment variables")

logger = logging.getLogger(__name__)

class DiscoveryHandler:
    """Handler for Discovery Mode interactions"""
    
    def __init__(self, model_handler, rag_handler):
        self.model_handler = model_handler
        self.rag_handler = rag_handler
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        logger.info("Initialized DiscoveryHandler")
    
    async def handle_suggestion_click(
        self,
        suggestion: str,
        model_name: str,
        use_rag: bool,
        rag_index: str
    ) -> List[Any]:
        """Handle suggestion chip click"""
        try:
            logger.info(f"Processing suggestion: {suggestion}")
            logger.info(f"Using model: {model_name}, RAG enabled: {use_rag}, RAG index: {rag_index}")
            
            # Get RAG context if enabled
            context = None
            if use_rag and self.rag_handler:
                try:
                    context = await self.rag_handler.get_relevant_context(suggestion)
                    logger.info(f"Retrieved RAG context: {context[:100]}..." if context else "No context found")
                except Exception as e:
                    logger.error(f"Error retrieving RAG context: {str(e)}")

            # Generate content using batch API calls
            content = await self._generate_all_sections(suggestion, model_name, context)
            logger.info("Generated content successfully")
            
            # Generate follow-up suggestions
            followups = await self._generate_followups(suggestion, content)
            logger.info(f"Generated {len(followups)} followup suggestions")
            
            # Create button updates
            button_updates = []
            for i in range(8):
                if i < len(followups):
                    button_updates.append(gr.update(value=followups[i], visible=True))
                else:
                    button_updates.append(gr.update(value="", visible=False))
            
            # Format content
            formatted_content = self._format_content(content)
            logger.info("Content formatted successfully")
            
            return [
                formatted_content["summary"],
                formatted_content["details"],
                formatted_content["bullets"],
                formatted_content["steps"],
                formatted_content["faq"],
                *button_updates,
                " → ".join([s.strip() for s in suggestion.split("→") if s.strip()])
            ]
            
        except Exception as e:
            logger.error(f"Error handling suggestion click: {str(e)}")
            return ["Error processing request"] * 5 + [gr.update(visible=False)] * 8 + [""]

    async def _generate_all_sections(
        self,
        topic: str,
        model_name: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate all content sections using batch API calls"""
        try:
            # Prepare prompts for each section
            prompts = self._get_section_prompts(topic, context)
            
            # Create tasks for concurrent execution
            tasks = []
            for section, prompt in prompts.items():
                task = self._generate_section(section, prompt, model_name)
                tasks.append(task)
            
            # Execute all tasks concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process responses
            result = {}
            for section, response in zip(prompts.keys(), responses):
                if isinstance(response, Exception):
                    logger.error(f"Error generating {section}: {str(response)}")
                    result[section] = f"Error generating {section}"
                else:
                    result[section] = response
            
            logger.info(f"Generated {len(result)} sections successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error generating sections: {str(e)}")
            return {}

    async def _generate_section(
        self,
        section: str,
        prompt: Dict[str, Any],
        model_name: str
    ) -> str:
        """Generate content for a single section"""
        try:
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]}
                ],
                temperature=0.7,
                max_tokens=prompt["max_tokens"]
            )
            
            if not response or not response.choices:
                logger.error(f"Empty response for section {section}")
                return f"Error: Failed to generate {section} content"
                
            content = response.choices[0].message.content
            if not content:
                logger.error(f"Empty content for section {section}")
                return f"Error: Empty {section} content"
                
            logger.info(f"Generated {section} content: {content[:100]}...")
            return content
            
        except Exception as e:
            logger.error(f"Error generating {section}: {str(e)}")
            return f"Error generating {section}: {str(e)}"

    def _get_section_prompts(self, topic: str, context: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Get prompts and parameters for each section"""
        context_note = f"\n\nUse this relevant context in your response:\n{context}" if context else ""
        
        base_system = """You are an AI assistant for San Francisco Bay University (SFBU).
Your responses should be:
- Accurate and based on provided context
- Professional yet engaging
- Well-structured and clear
- Specific to SFBU"""

        return {
            "summary": {
                "system": f"{base_system}\nGenerate a concise, engaging 2-3 sentence summary.{context_note}",
                "user": f"Summarize information about {topic} at SFBU.",
                "max_tokens": 150
            },
            "details": {
                "system": f"""{base_system}
Generate detailed information with proper formatting:
- Use ## for section headers
- Bold (**) key terms
- Use bullet points where appropriate
- Include 1-2 relevant emojis
- Add clear section breaks
- Include specific SFBU examples{context_note}""",
                "user": f"Provide detailed information about {topic} at SFBU.",
                "max_tokens": 1000
            },
            "bullets": {
                "system": f"""{base_system}
Generate 4-6 key points:
- Each point must be on a new line
- Start each point with a bullet point (•)
- Focus on most important information
- Include specific details
- Add a newline between points{context_note}""",
                "user": f"List the key points about {topic} at SFBU.",
                "max_tokens": 300
            },
            "steps": {
                "system": f"""{base_system}
Create a clear step-by-step guide:
- 4-5 actionable steps
- Number each step (1., 2., etc.)
- Be specific and practical
- Include any prerequisites
- Add a newline between steps{context_note}""",
                "user": f"Provide step-by-step guidance about {topic} at SFBU.",
                "max_tokens": 400
            },
            "faq": {
                "system": f"""{base_system}
Generate 3-4 frequently asked questions:
- Format each Q&A pair clearly
- Start questions with 'Q:' and answers with 'A:'
- Make questions practical and relevant
- Provide detailed, informative answers
- Add clear spacing between Q&A pairs
- Use markdown formatting
Example format:
Q: [Question here]?
A: [Detailed answer here.]

Q: [Next question]?
A: [Next answer.]{context_note}""",
                "user": f"Create a detailed FAQ section about {topic} at SFBU.",
                "max_tokens": 800
            },
            "suggestions": {
                "system": f"""{base_system}
Generate 6-8 follow-up suggestions:
- Each suggestion should be a complete sentence or question
- Make them relevant to {topic}
- Include both informational topics and practical questions
- Ensure variety in suggestion types
- Each suggestion should be clear and specific{context_note}""",
                "user": f"Generate follow-up suggestions related to {topic} at SFBU.",
                "max_tokens": 400
            }
        }

    def _format_content(self, content: Dict[str, Any]) -> Dict[str, str]:
        """Format content for display"""
        try:
            logger.info(f"Formatting content: {str(content)[:100]}...")
            
            # Handle string responses
            if isinstance(content, str):
                return {
                    "summary": "Error: Unexpected response format",
                    "details": content,
                    "bullets": "",
                    "steps": "",
                    "faq": ""
                }
            
            # Handle dictionary responses
            formatted = {}
            
            # Format summary
            summary = content.get("summary", "")
            formatted["summary"] = summary if isinstance(summary, str) else str(summary)
            
            # Format details
            details = content.get("details", "")
            formatted["details"] = self._format_details(details if isinstance(details, str) else str(details))
            
            # Format bullets
            bullets = content.get("bullets", [])
            if isinstance(bullets, str):
                bullets = [b.strip() for b in bullets.split('\n') if b.strip()]
            formatted["bullets"] = self._format_bullets(bullets if isinstance(bullets, list) else [])
            
            # Format steps
            steps = content.get("steps", [])
            if isinstance(steps, str):
                steps = [s.strip() for s in steps.split('\n') if s.strip()]
            formatted["steps"] = self._format_steps(steps if isinstance(steps, list) else [])
            
            # Format FAQ
            faq = content.get("faq", [])
            if isinstance(faq, str):
                # Try to parse string FAQ into structured format
                qa_pairs = []
                current_q = ""
                current_a = ""
                for line in faq.split('\n'):
                    line = line.strip()
                    if line.startswith(('Q:', 'Question:')):
                        if current_q:
                            qa_pairs.append({"question": current_q, "answer": current_a.strip()})
                        current_q = line.split(':', 1)[1].strip()
                        current_a = ""
                    elif line.startswith(('A:', 'Answer:')):
                        current_a = line.split(':', 1)[1].strip()
                    elif current_q:
                        current_a += " " + line
                if current_q:
                    qa_pairs.append({"question": current_q, "answer": current_a.strip()})
                faq = qa_pairs
            formatted["faq"] = self._format_faq(faq if isinstance(faq, list) else [])
            
            logger.info("Successfully formatted all content sections")
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting content: {str(e)}")
            return {
                "summary": "Error formatting content",
                "details": f"An error occurred while formatting the content: {str(e)}",
                "bullets": "",
                "steps": "",
                "faq": ""
            }

    def _format_details(self, text: str) -> str:
        """Format detailed information with markdown"""
        try:
            if not text:
                return ""
                
            # Clean up the text
            text = text.strip()
            
            # Ensure sections have proper headers
            sections = text.split('\n\n')
            formatted = []
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                    
                # If section doesn't start with header, add one
                if not section.startswith('#'):
                    # Try to create a header from first sentence
                    first_line = section.split('.')[0].strip()
                    rest = '.'.join(section.split('.')[1:]).strip()
                    if first_line:
                        section = f"## {first_line}\n\n{rest}" if rest else f"## {first_line}"
                
                formatted.append(section)
            
            return "\n\n".join(formatted)
            
        except Exception as e:
            logger.error(f"Error formatting details: {str(e)}")
            return str(text)

    def _format_bullets(self, points: List[str]) -> str:
        """Format bullet points"""
        try:
            if not points:
                return ""
                
            # Clean and format each point
            formatted_points = []
            for point in points:
                if isinstance(point, str) and point.strip():
                    # Remove existing bullet points or numbers
                    clean_point = point.strip().lstrip('•-*123456789.').strip()
                    # Add two newlines for better spacing
                    formatted_points.append(f"• {clean_point}\n")
            
            return "\n".join(formatted_points)
            
        except Exception as e:
            logger.error(f"Error formatting bullets: {str(e)}")
            return str(points)

    def _format_steps(self, steps: List[str]) -> str:
        """Format step-by-step guide"""
        try:
            if not steps:
                return ""
                
            # Clean and format each step
            formatted_steps = []
            for i, step in enumerate(steps, 1):
                if isinstance(step, str) and step.strip():
                    # Remove existing numbers or bullets
                    clean_step = step.strip().lstrip('•-*123456789.').strip()
                    formatted_steps.append(f"{i}. {clean_step}")
            
            return "\n".join(formatted_steps)
            
        except Exception as e:
            logger.error(f"Error formatting steps: {str(e)}")
            return str(steps)

    def _format_faq(self, faqs: List[Dict[str, str]]) -> str:
        """Format FAQ section"""
        try:
            if not faqs:
                return ""
                
            formatted_faqs = []
            for qa in faqs:
                if isinstance(qa, dict):
                    q = qa.get('question', '').strip()
                    a = qa.get('answer', '').strip()
                    if q and a:
                        # Add extra newlines for better spacing
                        formatted_faqs.append(f"**Q: {q}**\n\nA: {a}\n")
                elif isinstance(qa, str):
                    # Handle string FAQ entries
                    if ':' in qa:
                        parts = qa.split(':', 1)
                        q = parts[0].strip().lstrip('Q').lstrip('Question').strip()
                        a = parts[1].strip()
                        formatted_faqs.append(f"**Q: {q}**\n\nA: {a}\n")
                    else:
                        parts = qa.split('?', 1)
                        if len(parts) == 2:
                            q = parts[0].strip()
                            a = parts[1].strip()
                            formatted_faqs.append(f"**Q: {q}?**\n\nA: {a}\n")
            
            return "\n---\n\n".join(formatted_faqs) if formatted_faqs else ""
            
        except Exception as e:
            logger.error(f"Error formatting FAQ: {str(e)}")
            return str(faqs)

    async def _generate_followups(self, context: str, content: Dict[str, Any]) -> List[str]:
        """Generate contextual follow-up suggestions"""
        try:
            logger.info("Generating followup suggestions")
            
            # Get AI-generated suggestions
            suggestions = []
            
            # Get suggestions from content
            content_suggestions = content.get('suggestions', '')
            if isinstance(content_suggestions, str):
                # Split by newlines and clean up
                suggestions.extend([s.strip() for s in content_suggestions.split('\n') if s.strip()])
            elif isinstance(content_suggestions, list):
                suggestions.extend(content_suggestions)
            
            # Add RAG-based suggestions if available
            if self.rag_handler:
                try:
                    rag_context = await self.rag_handler.get_relevant_context(
                        query=context,
                        top_k=3
                    )
                    
                    if isinstance(rag_context, list):
                        for ctx in rag_context:
                            if isinstance(ctx, dict):
                                title = ctx.get('metadata', {}).get('title', '')
                                if title and len(title) > 10:
                                    suggestions.append(title)
                except Exception as e:
                    logger.error(f"Error processing RAG suggestions: {str(e)}")
            
            # Format and deduplicate suggestions
            formatted_suggestions = []
            emojis = ['📚', '🎓', '💡', '🔬', '📝', '🌟', '💼', '🤝']
            seen = set()
            
            for i, suggestion in enumerate(suggestions):
                if not isinstance(suggestion, str):
                    continue
                
                # Clean suggestion
                clean_text = suggestion.strip()
                clean_text = ' '.join([
                    word for word in clean_text.split()
                    if not any(char in word for char in ['📚', '🎓', '💡', '🔬', '📝', '🌟', '💼', '🤝', '🔍'])
                ]).strip()
                
                # Skip if too short or duplicate
                if len(clean_text) < 10 or clean_text.lower() in seen:
                    continue
                
                # Ensure it ends with proper punctuation
                if not clean_text.endswith(('.', '?', '!')):
                    clean_text += '.'
                
                # Add emoji and format
                formatted = f"{emojis[i % len(emojis)]} {clean_text}"
                formatted_suggestions.append(formatted)
                seen.add(clean_text.lower())
                
                # Limit to 8 suggestions
                if len(formatted_suggestions) >= 8:
                    break
            
            logger.info(f"Generated {len(formatted_suggestions)} unique followup suggestions")
            return formatted_suggestions
            
        except Exception as e:
            logger.error(f"Error generating followups: {str(e)}")
            return []