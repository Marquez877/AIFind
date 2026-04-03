from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class CustomerId:
    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise ValueError("CustomerId value must be UUID")

    @staticmethod
    def generate() -> "CustomerId":
        return CustomerId(value=uuid4())
