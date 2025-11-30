"""
Тесты для модуля code_extractor.py
"""

import pytest
from pathlib import Path
from src.code_extractor import (
    extract_code_entity,
    list_entities,
    EntityNotFoundError,
)


# Фикстура с тестовым Python файлом
@pytest.fixture
def sample_python_file(tmp_path):
    """Создаёт временный Python файл с функциями и классами для тестирования."""
    file_path = tmp_path / "test_module.py"
    content = '''"""Test module for code extraction."""


def simple_function():
    """Simple function without decorators."""
    return "Hello"


@pytest.fixture
def decorated_function():
    """Function with decorator."""
    return "World"


async def async_function():
    """Async function."""
    await something()
    return "Async"


class SimpleClass:
    """Simple class with methods."""

    def __init__(self):
        self.value = 0

    def method_one(self):
        """First method."""
        return self.value + 1

    @property
    def decorated_method(self):
        """Method with decorator."""
        return self.value * 2


class AnotherClass:
    """Another class."""

    async def async_method(self):
        """Async method in class."""
        await something()
        return "Done"
'''
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


class TestExtractCodeEntity:
    """Тесты для extract_code_entity()."""

    def test_extract_simple_function(self, sample_python_file):
        """Извлечение простой функции."""
        code = extract_code_entity(sample_python_file, "simple_function")

        assert "def simple_function():" in code
        assert 'return "Hello"' in code
        assert "Simple function without decorators" in code

    def test_extract_decorated_function(self, sample_python_file):
        """Извлечение функции с декоратором."""
        code = extract_code_entity(sample_python_file, "decorated_function")

        assert "@pytest.fixture" in code
        assert "def decorated_function():" in code
        assert 'return "World"' in code

    def test_extract_decorated_function_without_decorators(self, sample_python_file):
        """Извлечение функции без декораторов."""
        code = extract_code_entity(
            sample_python_file, "decorated_function", include_decorators=False
        )

        assert "@pytest.fixture" not in code
        assert "def decorated_function():" in code
        assert 'return "World"' in code

    def test_extract_async_function(self, sample_python_file):
        """Извлечение асинхронной функции."""
        code = extract_code_entity(sample_python_file, "async_function")

        assert "async def async_function():" in code
        assert "await something()" in code
        assert 'return "Async"' in code

    def test_extract_class(self, sample_python_file):
        """Извлечение класса целиком."""
        code = extract_code_entity(sample_python_file, "SimpleClass")

        assert "class SimpleClass:" in code
        assert "def __init__(self):" in code
        assert "def method_one(self):" in code
        assert "@property" in code
        assert "def decorated_method(self):" in code

    def test_extract_class_method(self, sample_python_file):
        """Извлечение метода класса."""
        code = extract_code_entity(sample_python_file, "SimpleClass.method_one")

        assert "def method_one(self):" in code
        assert "return self.value + 1" in code
        # Класс целиком НЕ должен быть в выводе
        assert "def __init__(self):" not in code

    def test_extract_decorated_method(self, sample_python_file):
        """Извлечение метода с декоратором."""
        code = extract_code_entity(sample_python_file, "SimpleClass.decorated_method")

        assert "@property" in code
        assert "def decorated_method(self):" in code
        assert "return self.value * 2" in code

    def test_extract_decorated_method_without_decorators(self, sample_python_file):
        """Извлечение метода без декоратора."""
        code = extract_code_entity(
            sample_python_file, "SimpleClass.decorated_method", include_decorators=False
        )

        assert "@property" not in code
        assert "def decorated_method(self):" in code

    def test_extract_async_class_method(self, sample_python_file):
        """Извлечение асинхронного метода класса."""
        code = extract_code_entity(sample_python_file, "AnotherClass.async_method")

        assert "async def async_method(self):" in code
        assert "await something()" in code
        assert 'return "Done"' in code

    def test_function_not_found(self, sample_python_file):
        """Обработка ошибки: функция не найдена."""
        with pytest.raises(EntityNotFoundError) as exc_info:
            extract_code_entity(sample_python_file, "nonexistent_function")

        error_message = str(exc_info.value)
        assert "nonexistent_function" in error_message
        assert "Доступные сущности" in error_message
        # Проверяем, что в сообщении есть список доступных функций
        assert "simple_function" in error_message

    def test_class_not_found(self, sample_python_file):
        """Обработка ошибки: класс не найден."""
        with pytest.raises(EntityNotFoundError) as exc_info:
            extract_code_entity(sample_python_file, "NonexistentClass.method")

        error_message = str(exc_info.value)
        assert "NonexistentClass" in error_message
        assert "Доступные классы" in error_message
        assert "SimpleClass" in error_message

    def test_method_not_found(self, sample_python_file):
        """Обработка ошибки: метод не найден в существующем классе."""
        with pytest.raises(EntityNotFoundError) as exc_info:
            extract_code_entity(sample_python_file, "SimpleClass.nonexistent_method")

        error_message = str(exc_info.value)
        assert "nonexistent_method" in error_message
        assert "SimpleClass" in error_message
        assert "Доступные методы" in error_message
        assert "method_one" in error_message

    def test_file_not_found(self):
        """Обработка ошибки: файл не существует."""
        with pytest.raises(FileNotFoundError):
            extract_code_entity("/nonexistent/path/file.py", "some_function")

    def test_syntax_error_in_file(self, tmp_path):
        """Обработка синтаксической ошибки в файле."""
        invalid_file = tmp_path / "invalid.py"
        invalid_file.write_text(
            "def broken(\n    # Missing closing parenthesis", encoding="utf-8"
        )

        with pytest.raises(SyntaxError):
            extract_code_entity(str(invalid_file), "broken")


class TestListEntities:
    """Тесты для list_entities()."""

    def test_list_all_entities(self, sample_python_file):
        """Получение списка всех сущностей в файле."""
        entities = list_entities(sample_python_file)

        # Проверка функций
        assert "simple_function" in entities["functions"]
        assert "decorated_function" in entities["functions"]
        assert "async_function" in entities["functions"]
        assert len(entities["functions"]) == 3

        # Проверка классов
        assert "SimpleClass" in entities["classes"]
        assert "AnotherClass" in entities["classes"]
        assert len(entities["classes"]) == 2

        # Проверка методов
        assert "method_one" in entities["methods"]["SimpleClass"]
        assert "decorated_method" in entities["methods"]["SimpleClass"]
        assert (
            len(entities["methods"]["SimpleClass"]) == 3
        )  # __init__, method_one, decorated_method

        assert "async_method" in entities["methods"]["AnotherClass"]
        assert len(entities["methods"]["AnotherClass"]) == 1

    def test_empty_file(self, tmp_path):
        """Список сущностей в пустом файле."""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("# Empty file\n", encoding="utf-8")

        entities = list_entities(str(empty_file))

        assert entities["functions"] == []
        assert entities["classes"] == []
        assert entities["methods"] == {}

    def test_file_not_found_list(self):
        """Обработка ошибки: файл не найден при листинге."""
        with pytest.raises(FileNotFoundError):
            list_entities("/nonexistent/file.py")


class TestIntegration:
    """Интеграционные тесты."""

    def test_extract_and_verify_code_executable(self, sample_python_file):
        """Проверка, что извлечённый код является валидным Python."""
        code = extract_code_entity(sample_python_file, "simple_function")

        # Пытаемся скомпилировать извлечённый код
        try:
            compile(code, "<extracted>", "exec")
        except SyntaxError:
            pytest.fail("Извлечённый код содержит синтаксические ошибки")

    def test_extract_multiple_entities(self, sample_python_file):
        """Извлечение нескольких сущностей из одного файла."""
        func_code = extract_code_entity(sample_python_file, "simple_function")
        class_code = extract_code_entity(sample_python_file, "SimpleClass")
        method_code = extract_code_entity(sample_python_file, "SimpleClass.method_one")

        assert "def simple_function()" in func_code
        assert "class SimpleClass:" in class_code
        assert "def method_one(self):" in method_code

        # Убеждаемся, что это разные куски кода
        assert func_code != class_code
        assert class_code != method_code
