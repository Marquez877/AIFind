# 🕯️ Голос из архива

Платформа для сохранения памяти о репрессированных жителях Кыргызстана (1918–1953).

## Запуск

```bash
cp .env.example .env   # добавить API ключи
./start.sh
```

**Готово:** http://localhost:8000

## API

| Swagger UI | http://localhost:8000/docs |
|------------|----------------------------|
| Health     | http://localhost:8000/health |

## Переменные (.env)

```env
ANTHROPIC_API_KEY=sk-ant-...   # обязательно
OPENAI_API_KEY=sk-...          # обязательно
```

## Команды

```bash
docker compose logs -f app     # логи
docker compose down            # остановить
docker compose down -v         # удалить данные
```

---

MIT • Хакатон 2026
