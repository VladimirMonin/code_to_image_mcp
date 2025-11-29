"""Конфигурация pytest."""

import pytest
from pathlib import Path


@pytest.fixture
def output_dir():
    """Директория для сохранения результатов тестов."""
    output = Path(__file__).parent / "output"
    output.mkdir(exist_ok=True)
    return output


@pytest.fixture
def test_plantuml_code():
    """Простой тестовый код PlantUML."""
    return """
@startuml
Alice -> Bob: Authentication Request
Bob --> Alice: Authentication Response
@enduml
"""


@pytest.fixture
def test_plantuml_code_cyrillic():
    """Тестовый код PlantUML с кириллицей."""
    return """
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
"""
