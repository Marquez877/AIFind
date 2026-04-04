#!/bin/bash
set -e

# ─────────────────────────────────────────────────────────────────────────────
# 🕯️ Голос из архива — Скрипт запуска
# ─────────────────────────────────────────────────────────────────────────────

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🕯️  Голос из архива — Запуск проекта${NC}"
echo ""

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker не установлен. Установите Docker: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker не запущен. Запустите Docker Desktop.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker доступен${NC}"

# Проверка .env файла
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo -e "${YELLOW}⚠ Файл .env не найден. Создаю из .env.example...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}⚠ Отредактируйте .env и добавьте API ключи (ANTHROPIC_API_KEY, OPENAI_API_KEY)${NC}"
    else
        echo -e "${RED}❌ Файлы .env и .env.example не найдены${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Файл .env найден${NC}"

# Остановка старых контейнеров (если есть)
echo ""
echo -e "${YELLOW}🔄 Останавливаю старые контейнеры...${NC}"
docker compose down 2>/dev/null || true

# Запуск контейнеров (миграции применяются автоматически)
echo ""
echo -e "${YELLOW}🚀 Запускаю контейнеры...${NC}"
echo -e "${YELLOW}   (миграции применяются автоматически перед запуском app)${NC}"
docker compose up -d --build

# Ожидание готовности приложения
echo ""
echo -e "${YELLOW}⏳ Ожидаю готовность приложения...${NC}"

MAX_RETRIES=60
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker compose ps app 2>/dev/null | grep -q "Up"; then
        break
    fi
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ Приложение не запустилось. Проверьте логи:${NC}"
    echo -e "${RED}   docker compose logs migrate${NC}"
    echo -e "${RED}   docker compose logs app${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Миграции применены, приложение запущено${NC}"

# Проверка health endpoint
echo ""
echo -e "${YELLOW}🏥 Проверяю работоспособность...${NC}"
sleep 3

HEALTH_CHECK=$(curl -s http://localhost:8000/health 2>/dev/null || echo "failed")
if echo "$HEALTH_CHECK" | grep -q "ok"; then
    echo -e "${GREEN}✓ Сервер работает!${NC}"
else
    echo -e "${RED}❌ Сервер не отвечает. Проверьте логи: docker compose logs app${NC}"
    exit 1
fi

# Готово
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Проект успешно запущен!${NC}"
echo ""
echo -e "   🌐 API:         http://localhost:8000"
echo -e "   📚 Swagger UI:  http://localhost:8000/docs"
echo -e "   📖 ReDoc:       http://localhost:8000/redoc"
echo ""
echo -e "   📋 Логи:        docker compose logs -f app"
echo -e "   🛑 Остановка:   docker compose down"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
