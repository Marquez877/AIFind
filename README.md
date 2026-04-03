# 🕯️ Голос из архива

> Верни имя забытому человеку

Платформа для сохранения памяти о репрессированных жителях Кыргызстана (1918–1953). Цифровой архив с ИИ-ассистентом, который помогает исследователям, журналистам и потомкам находить информацию в документах.

---

## 🚀 Быстрый старт

### Требования
- Docker & Docker Compose
- API-ключ Anthropic (Claude)

### Запуск

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd AIFind

# 2. Создать .env файл
cp .env.example .env
# Отредактировать .env и добавить ANTHROPIC_API_KEY

# 3. Запустить через Docker Compose
docker-compose up -d

# 4. Применить миграции
docker-compose exec app alembic upgrade head

# 5. Готово! API доступен на http://localhost:8000
```

### Проверка работы

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

---

## 📚 API Документация

После запуска доступна интерактивная документация:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🗂️ Основные эндпоинты

### Карточки репрессированных

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/v1/persons` | Создать карточку |
| `GET` | `/api/v1/persons` | Список карточек (с фильтрами) |
| `GET` | `/api/v1/persons/{id}` | Получить карточку |
| `PATCH` | `/api/v1/persons/{id}` | Обновить карточку |
| `DELETE` | `/api/v1/persons/{id}` | Удалить карточку |

**Фильтры для GET /api/v1/persons:**
- `?name=Асан` — поиск по имени
- `?region=Чуйская` — фильтр по региону
- `?accusation=враг` — фильтр по обвинению

### Документы

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/v1/persons/{id}/documents` | Загрузить документ (.txt/.md) |
| `GET` | `/api/v1/persons/{id}/documents` | Список документов |
| `GET` | `/api/v1/documents/{id}` | Получить документ |
| `DELETE` | `/api/v1/documents/{id}` | Удалить документ |

### ИИ-чат (RAG)

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/v1/persons/{id}/chat` | Задать вопрос по документам |

---

## 💡 Примеры использования

### Создание карточки

```bash
curl -X POST http://localhost:8000/api/v1/persons \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Байтемиров Асан",
    "birth_year": 1895,
    "death_year": 1937,
    "region": "Чуйская область",
    "accusation": "Враг народа",
    "biography": "Учитель из села Токмок. Арестован в 1937 году."
  }'
```

### Загрузка документа

```bash
curl -X POST http://localhost:8000/api/v1/persons/{person_id}/documents \
  -F "file=@document.txt"
```

### Вопрос ИИ-ассистенту

```bash
curl -X POST http://localhost:8000/api/v1/persons/{person_id}/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Когда был арестован этот человек?"}'
```

**Ответ:**
```json
{
  "answer": "Согласно документам, Асан Байтемиров был арестован в 1937 году...",
  "sources": ["document.txt"]
}
```

---

## ⚙️ Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|--------|
| `DATABASE_URL` | URL подключения к PostgreSQL | `postgresql+asyncpg://user:password@db:5432/assistant_db` |
| `ANTHROPIC_API_KEY` | API-ключ Anthropic Claude | `sk-ant-...` |
| `APP_ENV` | Окружение | `development` / `production` |

---

## 🏗️ Архитектура

```
app/
├── api/                    # HTTP слой
│   ├── v1/
│   │   ├── routers/        # Эндпоинты
│   │   └── schemas/        # Pydantic модели
│   └── dependencies.py     # Dependency Injection
├── domain/                 # Бизнес-логика
│   ├── entities/           # Доменные сущности
│   └── errors/             # Исключения
├── infrastructure/         # Внешние сервисы
│   ├── ai/                 # Claude клиент
│   ├── db/                 # SQLAlchemy модели
│   └── repositories/       # Реализации репозиториев
├── providers/              # Интерфейсы (ABC)
├── use_cases/              # Бизнес use cases
│   ├── persons/            # CRUD для карточек
│   ├── documents/          # Работа с документами
│   └── rag/                # RAG (чат с ИИ)
└── main.py                 # FastAPI приложение
```

### Clean Architecture
- **Entities** — чистые доменные объекты без зависимостей
- **Use Cases** — бизнес-логика приложения
- **Repositories** — абстракции для работы с данными
- **Infrastructure** — конкретные реализации (PostgreSQL, Claude API)

---

## 🛠️ Технологии

| Компонент | Технология |
|-----------|------------|
| Backend | Python 3.11+, FastAPI |
| База данных | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) |
| Миграции | Alembic |
| LLM | Anthropic Claude |
| Контейнеризация | Docker, Docker Compose |

---

## 📁 Структура проекта

```
AIFind/
├── alembic/                # Миграции БД
│   └── versions/
├── app/                    # Исходный код
├── docs/                   # Документация
├── .env.example            # Пример переменных окружения
├── docker-compose.yml      # Docker конфигурация
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🔧 Разработка

### Локальный запуск (без Docker)

```bash
# Создать виртуальное окружение
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.example .env
# Отредактировать .env

# Применить миграции
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload
```

### Создание миграции

```bash
alembic revision --autogenerate -m "описание изменений"
alembic upgrade head
```

---

## 📋 Функциональность

### ✅ Реализовано (Минимум)
- [x] Карточки репрессированных (ФИО, годы жизни, регион, обвинение, биография)
- [x] Проверка на дубликаты (имя + год рождения)
- [x] Поиск по имени, фильтрация по региону/обвинению
- [x] Загрузка документов (.txt, .md)
- [x] RAG: ответы ИИ на основе документов
- [x] Docker Compose для запуска одной командой

### 🎁 Бонусы
- [x] Docker Compose (+5 баллов)
- [x] Clean Architecture
- [ ] JWT-авторизация
- [ ] Векторные эмбеддинги
- [ ] SSE-стриминг ответов
- [ ] Unit-тесты

---

## 👥 Команда

**Хакатон 2026** — Кыргыз-Турк «Манас» Университет

---

## 📜 Лицензия

MIT

---

> «Тот, кто не знает своего прошлого, не имеет будущего.»
> — кыргызская пословица
