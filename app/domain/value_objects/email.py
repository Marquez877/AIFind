from dataclasses import dataclass
import re


_EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        normalized_value = self.value.strip().lower()
        if not normalized_value:
            raise ValueError("Email cannot be empty")
        if not _EMAIL_PATTERN.fullmatch(normalized_value):
            raise ValueError(f"Invalid email format: {self.value}")
        object.__setattr__(self, "value", normalized_value)

    def __str__(self) -> str:
        return self.value
