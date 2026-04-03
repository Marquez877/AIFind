from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    async def ask(
        self,
        history: list[dict[str, str]],  # [{'role': 'user'|'assistant', 'content': str}]
        user_message: str,
    ) -> str: ...
