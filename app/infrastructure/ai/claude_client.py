import anthropic
from typing import AsyncIterator

from app.providers.ai_provider import AIProvider


ARCHIVE_SYSTEM_PROMPT = """Ты — ИИ-ассистент архива репрессированных "Голос из архива".
Твоя задача — отвечать на вопросы ТОЛЬКО на основе предоставленных документов.

Правила:
1. Отвечай ТОЛЬКО на основе информации из документов
2. Если информации нет в документах — честно скажи: "В предоставленных документах нет информации об этом"
3. Цитируй документы, когда это уместно
4. Будь точен в датах, именах и фактах
5. Отвечай на русском языке
6. Будь уважителен к памяти репрессированных людей
"""


class ClaudeClient(AIProvider):
    def __init__(self, api_key: str):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def ask(self, history: list[dict], user_message: str) -> str:
        messages: list[dict] = [*history, {"role": "user", "content": user_message}]

        try:
            response = await self._client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system="You are a helpful business support assistant. Answer clearly and professionally.",
                messages=messages,
            )
        except anthropic.APIError as exc:
            raise RuntimeError(f"Anthropic API request failed: {exc}") from exc

        return response.content[0].text

    async def ask_with_context(self, context: str, question: str) -> str:
        """Ответить на вопрос на основе документов (RAG)."""
        user_message = f"""Документы из архива:

{context}

---

Вопрос: {question}

Ответь на основе документов выше:"""

        try:
            response = await self._client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=ARCHIVE_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
        except anthropic.APIError as exc:
            raise RuntimeError(f"Anthropic API request failed: {exc}") from exc

        return response.content[0].text

    async def ask_with_context_stream(
        self,
        context: str,
        question: str,
    ) -> AsyncIterator[str]:
        """Стримить ответ на вопрос на основе документов (RAG)."""
        user_message = f"""Документы из архива:

{context}

---

Вопрос: {question}

Ответь на основе документов выше:"""

        try:
            async with self._client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=ARCHIVE_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            ) as stream:
                async for text in stream.text_stream:
                    if text:
                        yield text
        except anthropic.APIError as exc:
            raise RuntimeError(f"Anthropic API streaming request failed: {exc}") from exc
