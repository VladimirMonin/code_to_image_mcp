#!/usr/bin/env python3
"""Тест PlantUML с кириллицей и разными форматами."""

from diagram_renderer import render_diagram_from_string
from pathlib import Path

# Тестовые диаграммы
test_cases = [
    {
        "name": "Кириллица - Последовательность",
        "code": """
@startuml
participant "Пользователь" as User
participant "Сервер" as Server
participant "База данных" as DB

User -> Server: Запрос авторизации
activate Server

Server -> DB: Проверка учётных данных
activate DB
DB --> Server: Данные пользователя
deactivate DB

Server --> User: Токен доступа
deactivate Server
@enduml
""",
        "format": "png",
    },
    {
        "name": "Кириллица - Классы",
        "code": """
@startuml
class Пользователь {
  -имя: str
  -email: str
  +войти()
  +выйти()
}

class Заказ {
  -номер: int
  -сумма: float
  +создать()
  +отменить()
}

Пользователь "1" -- "*" Заказ : создаёт >
@enduml
""",
        "format": "svg",
    },
    {
        "name": "Activity - Mixed",
        "code": """
@startuml
start
:Начало процесса;
if (Условие выполнено?) then (да)
  :Выполнить действие А;
else (нет)
  :Выполнить действие Б;
endif
:Завершение;
stop
@enduml
""",
        "format": "png",
    },
]

print("=== Тестирование PlantUML с кириллицей ===\n")

output_dir = Path("/tmp/plantuml_tests")
output_dir.mkdir(exist_ok=True)

for i, test in enumerate(test_cases, 1):
    print(f"{i}. Тест: {test['name']}")
    print(f"   Формат: {test['format']}")

    output_file = output_dir / f"test_{i}.{test['format']}"

    try:
        result = render_diagram_from_string(
            diagram_code=test["code"],
            output_path=str(output_file),
            format=test["format"],
            theme_name="default",
        )

        if result["success"]:
            print(f"   ✓ Создано: {result['output_path']}")
            print(f"     Размер: {result['file_size_kb']} KB")
        else:
            print(f"   ✗ Ошибка: {result.get('error')}")

    except Exception as e:
        print(f"   ✗ Исключение: {e}")

    print()

print(f"\nВсе тесты завершены. Результаты в: {output_dir}")
