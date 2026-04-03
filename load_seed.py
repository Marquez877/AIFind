import json
import requests

# Загрузить данные
with open("docs/seed.json", "r", encoding="utf-8") as f:
    persons = json.load(f)

# Отправить каждую карточку
for person in persons:
    data = {
        "full_name": person["full_name"],
        "birth_year": person["birth_year"],
        "death_year": person.get("death_year"),
        "region": person["region"],
        "accusation": person["charge"],
        "biography": person["biography"]
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/persons",
        json=data
    )
    
    if response.status_code == 201:
        print(f"✓ Создано: {person['full_name']}")
    elif response.status_code == 409:
        print(f"⚠ Уже существует: {person['full_name']}")
    else:
        print(f"✗ Ошибка: {person['full_name']} - {response.text}")

print("\nГотово!")