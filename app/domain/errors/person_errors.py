from uuid import UUID


class PersonNotFoundError(Exception):
    """Исключение: карточка репрессированного не найдена."""

    def __init__(self, person_id: UUID) -> None:
        self.person_id = person_id
        super().__init__(f"Person with id {person_id} not found")


class PersonAlreadyExistsError(Exception):
    """Исключение: карточка с такими данными уже существует (дубль)."""

    def __init__(self, full_name: str, birth_year: int, existing_id: UUID) -> None:
        self.full_name = full_name
        self.birth_year = birth_year
        self.existing_id = existing_id
        super().__init__(
            f"Person '{full_name}' born in {birth_year} already exists (id: {existing_id})"
        )
