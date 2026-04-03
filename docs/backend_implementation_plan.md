# План реализации бекенда — «Голос из архива»

> Анализ текущего состояния + поэтапный путь к минимальным требованиям

---

## 📊 ТЕКУЩЕЕ СОСТОЯНИЕ ПРОЕКТА

### ✅ Что уже реализовано

| Компонент | Статус | Описание |
|-----------|--------|----------|
| FastAPI приложение | ✅ Готово | `app/main.py` с CORS, health check |
| PostgreSQL + Docker Compose | ✅ Готово | `docker-compose.yml` с healthcheck |
| Alembic миграции | ✅ Готово | Настроен, есть initial migration |
| Clean Architecture | ✅ Готово | domain/entities, use_cases, repositories |
| Anthropic Claude интеграция | ✅ Готово | `claude_client.py` с async |
| CRUD для Customers | ✅ Готово | Create, Read, Update, Delete, List |
| Conversations + Messages | ✅ Готово | Чат с историей сообщений |
| Проверка дублей (email) | ✅ Готово | `CustomerAlreadyExistsError` |
| Поиск по имени/компании | ✅ Готово | `list_customers` с фильтрами |

### ❌ Что НЕ соответствует требованиям хакатона

| Проблема | Текущее состояние | Требование |
|----------|-------------------|------------|
| **Модель данных** | `Customer` (клиент бизнеса) | `Person` (репрессированный) |
| **Поля карточки** | name, email, phone, company | имя, годы жизни, регион, обвинение, биография |
| **Проверка дублей** | По email | По имени + году рождения |
| **Загрузка документов** | ❌ Нет | POST `.txt`/`.md` |
| **RAG** | Общий ассистент без документов | Ответы на основе загруженных документов |
| **Привязка чата** | К customer | К person + его документам |

---

## 🎯 МИНИМАЛЬНЫЕ ТРЕБОВАНИЯ (обязательные)

По условиям хакатона, **без этого проект НЕ допускается к оценке**:

1. ☐ Карточка человека (имя, годы жизни, регион, обвинение, биография)
2. ☐ Проверка дублей (имя + год рождения)
3. ☐ Поиск по имени, фильтр по региону/категории
4. ☐ Загрузка документов `.txt`/`.md`
5. ☐ RAG: передача документов в LLM с вопросом
6. ☐ Чат: вопрос → ответ на основе документов
7. ☐ README с инструкцией запуска

---

## 🔧 ПЛАН ДЕЙСТВИЙ

### Этап 1: Модель Person (репрессированный) — 1.5 часа

#### 1.1 Создать entity `Person`
**Файл:** `app/domain/entities/person.py`

```python
@dataclass(frozen=True)
class Person:
    id: UUID
    full_name: str          # ФИО
    birth_year: int         # Год рождения
    death_year: int | None  # Год смерти (может быть неизвестен)
    region: str             # Регион
    accusation: str         # Обвинение
    biography: str          # Краткое описание/биография
    created_at: datetime
    updated_at: datetime
```

#### 1.2 Создать SQLAlchemy модель `PersonModel`
**Файл:** `app/infrastructure/db/models.py` — добавить:

```python
class PersonModel(Base):
    __tablename__ = "persons"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    birth_year: Mapped[int] = mapped_column(Integer, nullable=False)
    death_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    region: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    accusation: Mapped[str] = mapped_column(String(500), nullable=False)
    biography: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    documents: Mapped[list["DocumentModel"]] = relationship(back_populates="person", cascade="all, delete-orphan")
```

#### 1.3 Создать модель `DocumentModel`
```python
class DocumentModel(Base):
    __tablename__ = "documents"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    person_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("persons.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    person: Mapped["PersonModel"] = relationship(back_populates="documents")
```

#### 1.4 Создать миграцию Alembic
```bash
alembic revision --autogenerate -m "add_persons_and_documents"
alembic upgrade head
```

---

### Этап 2: Repository и Use Cases для Person — 1.5 часа

#### 2.1 Создать `PersonRepository`
**Файл:** `app/providers/person_repository.py`

```python
class PersonRepository(Protocol):
    async def get_by_id(self, id: UUID) -> Person | None: ...
    async def list(self, name: str | None, region: str | None, accusation: str | None, limit: int, offset: int) -> list[Person]: ...
    async def find_duplicate(self, full_name: str, birth_year: int) -> Person | None: ...
    async def save(self, person: Person) -> Person: ...
    async def delete(self, id: UUID) -> None: ...
```

#### 2.2 Создать Use Cases
- `CreatePersonUseCase` — с проверкой на дубли (имя + год рождения)
- `GetPersonUseCase`
- `ListPersonsUseCase` — с фильтрами по имени, региону, обвинению
- `UpdatePersonUseCase`
- `DeletePersonUseCase`

#### 2.3 Ошибки
**Файл:** `app/domain/errors/__init__.py`

```python
class PersonNotFoundError(Exception): ...
class PersonAlreadyExistsError(Exception): ...  # Для дублей
```

---

### Этап 3: API для Person — 1 час

#### 3.1 Создать роутер
**Файл:** `app/api/v1/routers/persons_router.py`

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/persons` | Создать карточку (с проверкой дублей) |
| GET | `/api/v1/persons` | Список с фильтрами (?name=&region=&accusation=) |
| GET | `/api/v1/persons/{id}` | Получить одну карточку |
| PATCH | `/api/v1/persons/{id}` | Обновить карточку |
| DELETE | `/api/v1/persons/{id}` | Удалить карточку |

#### 3.2 Pydantic схемы
**Файл:** `app/api/v1/schemas/person_schemas.py`

```python
class PersonCreateRequest(BaseModel):
    full_name: str
    birth_year: int
    death_year: int | None = None
    region: str
    accusation: str
    biography: str

class PersonResponse(BaseModel):
    id: UUID
    full_name: str
    birth_year: int
    death_year: int | None
    region: str
    accusation: str
    biography: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

---

### Этап 4: Загрузка документов — 1 час

#### 4.1 Создать entity `Document`
**Файл:** `app/domain/entities/document.py`

```python
@dataclass(frozen=True)
class Document:
    id: UUID
    person_id: UUID
    filename: str
    content: str
    uploaded_at: datetime
```

#### 4.2 API эндпоинты
**Файл:** `app/api/v1/routers/documents_router.py`

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/persons/{person_id}/documents` | Загрузить `.txt`/`.md` файл |
| GET | `/api/v1/persons/{person_id}/documents` | Список документов карточки |
| GET | `/api/v1/documents/{document_id}` | Получить содержимое документа |
| DELETE | `/api/v1/documents/{document_id}` | Удалить документ |

#### 4.3 Валидация файлов
```python
ALLOWED_EXTENSIONS = {".txt", ".md"}

@router.post("/persons/{person_id}/documents")
async def upload_document(
    person_id: UUID,
    file: UploadFile = File(...),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Только {ALLOWED_EXTENSIONS} файлы")
    
    content = (await file.read()).decode("utf-8")
    # Сохранить в БД...
```

---

### Этап 5: RAG — Чат на основе документов — 2 часа

#### 5.1 Изменить system prompt в `claude_client.py`

```python
ARCHIVE_SYSTEM_PROMPT = """Ты — ИИ-ассистент архива репрессированных "Голос из архива".
Твоя задача — отвечать на вопросы ТОЛЬКО на основе предоставленных документов.

Правила:
1. Если информации нет в документах — честно скажи об этом
2. Цитируй документы, когда возможно
3. Будь точен в датах и именах
4. Отвечай на русском языке
"""
```

#### 5.2 Создать RAG Use Case
**Файл:** `app/use_cases/rag/ask_question.py`

```python
class AskQuestionUseCase:
    def __init__(self, person_repo, document_repo, ai_provider):
        ...
    
    async def execute(self, person_id: UUID, question: str) -> dict:
        # 1. Проверить что person существует
        person = await self._person_repo.get_by_id(person_id)
        if not person:
            raise PersonNotFoundError(person_id)
        
        # 2. Получить все документы
        documents = await self._document_repo.get_by_person_id(person_id)
        if not documents:
            return {"answer": "Для этой карточки нет загруженных документов.", "sources": []}
        
        # 3. Собрать контекст
        context = "\n\n---\n\n".join([
            f"Документ: {doc.filename}\n{doc.content}" 
            for doc in documents
        ])
        
        # 4. Сформировать prompt
        prompt = f"""Контекст (документы из архива):

{context}

---

Вопрос пользователя: {question}

Ответь на основе документов выше:"""
        
        # 5. Вызвать LLM
        answer = await self._ai_provider.ask([], prompt)
        
        return {
            "answer": answer,
            "sources": [doc.filename for doc in documents]
        }
```

#### 5.3 API эндпоинт для RAG
**Файл:** `app/api/v1/routers/chat_router.py`

```python
@router.post("/persons/{person_id}/chat")
async def ask_question(
    person_id: UUID,
    payload: ChatRequest,
    use_case: AskQuestionUseCase = Depends(get_ask_question_uc),
):
    result = await use_case.execute(person_id, payload.question)
    return ChatResponse(**result)
```

---

### Этап 6: Финализация — 1 час

#### 6.1 Обновить `main.py`
```python
from app.api.v1.routers import persons_router, documents_router, chat_router

app.include_router(persons_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
```

#### 6.2 Обновить README.md
```markdown
# Голос из архива — Backend

## Быстрый старт

1. Склонировать репозиторий
2. Создать `.env` файл:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/assistant_db
   ANTHROPIC_API_KEY=your_key_here
   ```
3. Запустить:
   ```bash
   docker-compose up -d
   ```
4. Применить миграции:
   ```bash
   alembic upgrade head
   ```
5. Сервер доступен: http://localhost:8000

## API Endpoints

### Карточки репрессированных
- `POST /api/v1/persons` — создать карточку
- `GET /api/v1/persons?name=&region=&accusation=` — поиск
- `GET /api/v1/persons/{id}` — получить карточку

### Документы
- `POST /api/v1/persons/{id}/documents` — загрузить .txt/.md
- `GET /api/v1/persons/{id}/documents` — список документов

### ИИ-чат (RAG)
- `POST /api/v1/persons/{id}/chat` — задать вопрос по документам
```

---

## 📋 ЧЕКЛИСТ МИНИМУМА

| # | Требование | Файлы для изменения | Статус |
|---|------------|---------------------|--------|
| 1 | Карточка Person (имя, годы, регион, обвинение, биография) | `entities/person.py`, `models.py`, миграция | ☐ |
| 2 | Проверка дублей (имя + год рождения) | `person_repository.py`, `create_person.py` | ☐ |
| 3 | Поиск по имени, фильтр по региону/обвинению | `persons_router.py`, `list_persons.py` | ☐ |
| 4 | Загрузка `.txt`/`.md` документов | `documents_router.py`, `document_repository.py` | ☐ |
| 5 | RAG: документы → LLM → ответ | `ask_question.py`, `claude_client.py` | ☐ |
| 6 | Чат: вопрос → ответ на основе документов | `chat_router.py` | ☐ |
| 7 | README с инструкцией | `README.md` | ☐ |

---

## ⏱️ ПРИМЕРНЫЙ ТАЙМИНГ

| Этап | Время | Результат |
|------|-------|-----------|
| 1. Модель Person + миграция | 1.5 ч | БД готова |
| 2. Repository + Use Cases | 1.5 ч | Бизнес-логика |
| 3. API для Person | 1 ч | CRUD работает |
| 4. Загрузка документов | 1 ч | Файлы сохраняются |
| 5. RAG (чат с документами) | 2 ч | ИИ отвечает |
| 6. Финализация + README | 1 ч | Готово к демо |
| **ИТОГО** | **~8 ч** | **Минимум выполнен** |

---

## 🏆 БОНУСНЫЕ ФУНКЦИИ (после минимума!)

| Функция | Баллы | Сложность |
|---------|-------|-----------|
| Docker Compose (уже есть!) | +5 | ✅ Готово |
| История диалогов (уже есть!) | +3 | ✅ Готово |
| Unit-тесты (5 штук) | +3 | Средняя |
| SSE-стриминг ответа | +3 | Средняя |
| JWT-авторизация | +5 | Высокая |

---

## ⚠️ ВАЖНО

1. **Не трогайте Customer/Conversation** пока — это отдельная функциональность
2. **Сначала минимум** — бонусы потом
3. **Тестируйте каждый этап** перед переходом к следующему
4. **Docker Compose уже даёт +5 баллов** — он работает!
5. **Коммитьте часто** — это влияет на оценку

---

**Текущий прогресс: ~40% инфраструктуры готово**
**Осталось: ~60% специфичной логики для хакатона**
