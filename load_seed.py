#!/usr/bin/env python3
"""
Загрузка seed данных в базу.
Проверяет дубликаты по имени + году рождения, не создаёт повторно.

Использование:
  python load_seed.py                    # локально
  python load_seed.py --url http://app:8000  # внутри Docker
"""

import asyncio
import json
import sys
from pathlib import Path
from uuid import uuid4

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.infrastructure.db.models import PersonModel


async def load_seed_data():
    """Загрузить seed данные напрямую в БД с проверкой дублей."""
    
    # Путь к seed файлу
    seed_path = Path(__file__).parent / "docs" / "seed.json"
    if not seed_path.exists():
        print(f"❌ Файл не найден: {seed_path}")
        return
    
    # Загрузить JSON
    with open(seed_path, "r", encoding="utf-8") as f:
        persons_data = json.load(f)
    
    print(f"📂 Загружено {len(persons_data)} записей из seed.json")
    
    # Подключение к БД
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    created = 0
    skipped = 0
    errors = 0
    
    async with async_session() as session:
        for person in persons_data:
            full_name = person["full_name"].strip()
            birth_year = person["birth_year"]
            
            # Проверить существует ли запись с таким именем и годом
            result = await session.execute(
                select(PersonModel).where(
                    PersonModel.full_name == full_name,
                    PersonModel.birth_year == birth_year
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"⏭️  Пропуск (уже есть): {full_name} ({birth_year})")
                skipped += 1
                continue
            
            # Маппинг полей seed.json → PersonModel
            try:
                new_person = PersonModel(
                    id=uuid4(),
                    full_name=full_name,
                    birth_year=birth_year,
                    death_year=person.get("death_year"),
                    region=person.get("region", "Неизвестно"),
                    accusation=person.get("charge", person.get("accusation", "Не указано")),
                    biography=person.get("biography", ""),
                    verification_status=person.get("status", "pending"),
                )
                session.add(new_person)
                await session.commit()
                print(f"✅ Создано: {full_name} ({birth_year})")
                created += 1
            except Exception as e:
                await session.rollback()
                print(f"❌ Ошибка: {full_name} - {e}")
                errors += 1
    
    await engine.dispose()
    
    print("\n" + "=" * 50)
    print(f"📊 Итого:")
    print(f"   ✅ Создано: {created}")
    print(f"   ⏭️  Пропущено (дубли): {skipped}")
    print(f"   ❌ Ошибок: {errors}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(load_seed_data())