"""
Модуль для извлечения кода из Python файлов с использованием AST.

Позволяет точечно извлекать функции, классы и методы из больших файлов
без необходимости читать весь файл целиком.
"""

import ast
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class EntityNotFoundError(Exception):
    """Исключение, когда запрашиваемая сущность не найдена в файле."""

    pass


def extract_code_entity(
    file_path: str, entity_name: str, include_decorators: bool = True
) -> str:
    """
    Извлекает исходный код функции, класса или метода из Python файла.

    Использует AST для точного поиска сущности и возвращает её исходный код,
    включая декораторы (если указано).

    Args:
        file_path: Абсолютный путь к Python файлу.
        entity_name: Имя сущности для извлечения:
            - "function_name" - для функции
            - "ClassName" - для класса
            - "ClassName.method_name" - для метода класса
        include_decorators: Включать декораторы в извлечённый код.

    Returns:
        Исходный код сущности как строка.

    Raises:
        FileNotFoundError: Если файл не существует.
        SyntaxError: Если файл содержит синтаксические ошибки Python.
        EntityNotFoundError: Если сущность не найдена в файле.

    Example:
        >>> code = extract_code_entity("app.py", "calculate_total")
        >>> code = extract_code_entity("models.py", "Order.validate")
    """
    logger.debug(f"🔍 Извлечение '{entity_name}' из {file_path}")

    # Проверка существования файла
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    # Чтение файла
    with open(path, "r", encoding="utf-8") as f:
        source_code = f.read()
        source_lines = source_code.splitlines(keepends=True)

    # Парсинг в AST
    try:
        tree = ast.parse(source_code, filename=str(path))
    except SyntaxError as e:
        logger.error(f"❌ Синтаксическая ошибка в {file_path}: {e}")
        raise

    # Определяем, ищем ли метод класса (формат "ClassName.method_name")
    if "." in entity_name:
        class_name, method_name = entity_name.split(".", 1)
        logger.debug(f"🔍 Поиск метода '{method_name}' в классе '{class_name}'")
        return _extract_class_method(
            tree, source_lines, class_name, method_name, include_decorators
        )
    else:
        # Ищем функцию или класс верхнего уровня
        logger.debug(f"🔍 Поиск функции/класса '{entity_name}' верхнего уровня")
        return _extract_top_level_entity(
            tree, source_lines, entity_name, include_decorators
        )


def _extract_top_level_entity(
    tree: ast.Module,
    source_lines: list[str],
    entity_name: str,
    include_decorators: bool,
) -> str:
    """
    Извлекает функцию или класс верхнего уровня.

    Args:
        tree: AST дерево модуля.
        source_lines: Строки исходного кода.
        entity_name: Имя функции или класса.
        include_decorators: Включать декораторы.

    Returns:
        Исходный код сущности.

    Raises:
        EntityNotFoundError: Если сущность не найдена.
    """
    for node in ast.walk(tree):
        # Ищем только определения верхнего уровня
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == entity_name:
                # Нашли! Извлекаем код
                start_line = _get_start_line(node, include_decorators)
                end_line = node.end_lineno

                logger.info(
                    f"✅ Найдена сущность '{entity_name}' (строки {start_line}-{end_line})"
                )

                # Извлекаем строки (AST использует 1-based индексацию)
                code = "".join(source_lines[start_line - 1 : end_line])
                return code

    # Не нашли - формируем список доступных сущностей
    available = _list_available_entities(tree)
    error_msg = (
        f"Сущность '{entity_name}' не найдена в файле.\n"
        f"Доступные сущности верхнего уровня: {', '.join(available)}"
    )
    logger.error(f"❌ {error_msg}")
    raise EntityNotFoundError(error_msg)


def _extract_class_method(
    tree: ast.Module,
    source_lines: list[str],
    class_name: str,
    method_name: str,
    include_decorators: bool,
) -> str:
    """
    Извлекает метод из класса.

    Args:
        tree: AST дерево модуля.
        source_lines: Строки исходного кода.
        class_name: Имя класса.
        method_name: Имя метода.
        include_decorators: Включать декораторы.

    Returns:
        Исходный код метода.

    Raises:
        EntityNotFoundError: Если класс или метод не найдены.
    """
    # Ищем класс
    class_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            class_node = node
            break

    if class_node is None:
        available_classes = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        ]
        error_msg = (
            f"Класс '{class_name}' не найден.\n"
            f"Доступные классы: {', '.join(available_classes)}"
        )
        logger.error(f"❌ {error_msg}")
        raise EntityNotFoundError(error_msg)

    # Ищем метод внутри класса
    for node in class_node.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == method_name:
                start_line = _get_start_line(node, include_decorators)
                end_line = node.end_lineno

                logger.info(
                    f"✅ Найден метод '{class_name}.{method_name}' (строки {start_line}-{end_line})"
                )

                code = "".join(source_lines[start_line - 1 : end_line])
                return code

    # Метод не найден
    available_methods = [
        node.name
        for node in class_node.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    error_msg = (
        f"Метод '{method_name}' не найден в классе '{class_name}'.\n"
        f"Доступные методы: {', '.join(available_methods)}"
    )
    logger.error(f"❌ {error_msg}")
    raise EntityNotFoundError(error_msg)


def _get_start_line(node: ast.AST, include_decorators: bool) -> int:
    """
    Определяет начальную строку сущности с учётом декораторов.

    Args:
        node: AST узел функции/класса.
        include_decorators: Включать декораторы.

    Returns:
        Номер начальной строки (1-based).
    """
    if include_decorators and hasattr(node, "decorator_list") and node.decorator_list:
        # Берём строку первого декоратора
        return node.decorator_list[0].lineno
    else:
        # Берём строку определения функции/класса
        return node.lineno


def _list_available_entities(tree: ast.Module) -> list[str]:
    """
    Возвращает список доступных сущностей верхнего уровня в модуле.

    Args:
        tree: AST дерево модуля.

    Returns:
        Список имён функций и классов.
    """
    entities = []
    for node in tree.body:  # Только верхний уровень
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            entities.append(node.name)
    return entities


def list_entities(file_path: str) -> dict[str, list[str]]:
    """
    Возвращает структурированный список всех сущностей в файле.

    Args:
        file_path: Абсолютный путь к Python файлу.

    Returns:
        Словарь с ключами:
            - "functions": список имён функций верхнего уровня
            - "classes": список имён классов
            - "methods": словарь {class_name: [method1, method2, ...]}

    Raises:
        FileNotFoundError: Если файл не существует.
        SyntaxError: Если файл содержит синтаксические ошибки.

    Example:
        >>> entities = list_entities("models.py")
        >>> print(entities["classes"])
        ['Order', 'Customer']
        >>> print(entities["methods"]["Order"])
        ['validate', 'calculate_total', 'save']
    """
    logger.debug(f"📋 Список сущностей в {file_path}")

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        source_code = f.read()

    tree = ast.parse(source_code, filename=str(path))

    functions = []
    classes = []
    methods = {}

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
            # Собираем методы класса
            class_methods = [
                method.name
                for method in node.body
                if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            methods[node.name] = class_methods

    logger.info(f"✅ Найдено: {len(functions)} функций, {len(classes)} классов")

    return {"functions": functions, "classes": classes, "methods": methods}
