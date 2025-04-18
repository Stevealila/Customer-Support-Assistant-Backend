import json
from typing import AsyncGenerator, Dict, List

import groq

from app.core.config import settings
from app.templates.prompts import support_prompt_template


class AIService:
    def __init__(self):
        self.client = groq.AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL_NAME

    async def generate_response_stream(
        self, ticket_description: str, message_history: List[Dict], latest_message: str
    ) -> AsyncGenerator[str, None]:
        # Format the prompt using the template
        prompt = support_prompt_template.format(
            ticket_description=ticket_description,
            message_history=self._format_message_history(message_history),
            latest_message=latest_message,
        )

        # Generate streaming response from Groq
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=2048,
        )

        # Yield chunks as they come in
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _format_message_history(self, messages: List[Dict]) -> str:
        if not messages:
            return "No previous messages"
        
        formatted_history = ""
        for msg in messages:
            sender_type = "AI assistant" if msg["is_ai"] else "Customer"
            formatted_history += f"{sender_type}: {msg['content']}\n"
        
        return formatted_history.strip()