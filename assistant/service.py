import os
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Use a mock/stub implementation if no real API key is provided
# For a real implementation, you might use 'openai' or 'anthropic' packages.
class AILearningAssistant:
    def __init__(self):
        self.api_key = os.environ.get('AI_PROVIDER_API_KEY')
        self.is_configured = bool(self.api_key)
        
    def generate_response(self, system_prompt, messages, max_tokens=500):
        """
        messages format: [{'role': 'user'|'assistant', 'content': '...'}, ...]
        """
        if not self.is_configured:
            from .local_bot import LocalBotEngine
            local_bot = LocalBotEngine()
            
            # Extract last user message and context
            last_msg = messages[-1]['content'] if messages else ""
            
            # We don't have subject and language strictly in `generate_response` arguments unless we parse system_prompt, 
            # but we can try to extract it from system_prompt
            subject = "Mathematics"
            if "English" in system_prompt and "Mathematics" not in system_prompt:
                subject = "English"
                
            language = "English"
            if "Kannada" in system_prompt:
                language = "Kannada"
                
            return local_bot.get_response(last_msg, subject=subject, language=language)
            
            
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=self.api_key)
            
            # Convert messages to Gemini format
            formatted_messages = []
            for msg in messages:
                # Gemini roles are "user" and "model"
                role = "user" if msg['role'] == "user" else "model"
                formatted_messages.append(
                    {"role": role, "parts": [{"text": msg['content']}]}
                )
                
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=formatted_messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    max_output_tokens=max_tokens,
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"AI Provider error: {e}")
            raise Exception("I'm currently experiencing technical difficulties connecting to the AI provider. Please try again later.")
            
    def construct_system_prompt(self, subject, grade, language, context=None):
        prompt = (
            f"You are the Concept Compass AI Learning Assistant, a helpful and encouraging "
            f"tutor for Grade {grade} students studying {subject}. "
            f"You must communicate in {language}. "
            "Use clear, age-appropriate language. Avoid inventing curriculum facts. "
            "Preserve mathematical notation clearly. "
            "If you recommend studying a topic, you can provide markdown links like this: "
            "`[Study <Topic>](/learning/lesson/<concept_id>/)` or `[Practice <Topic>](/learning/practice/<concept_id>/)`. "
            "If they should add it to their daily plan, link to `[Study Plan](/progress/plan/)`."
        )
        if context:
            prompt += f"\n\nContext:\n{context}"
        return prompt
