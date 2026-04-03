import anthropic

from app.providers.ai_provider import AIProvider


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
