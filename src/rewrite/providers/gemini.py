"""Google Gemini provider — uses API key."""

from __future__ import annotations

from google import genai

from rewrite.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    """Gemini provider authenticated with an API key."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def rewrite(self, text: str, system_prompt: str = "") -> str:
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=text,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
            ),
        )
        return response.text or text
