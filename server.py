#!/usr/bin/env python3
"""MCP сервер для генерации скриншотов кода и диаграмм.

Предоставляет инструменты для:
- Генерации скриншотов кода из строки и файла
- Извлечения и скриншотинга конкретных функций/классов из файлов (AST)
- Генерации UML диаграмм через PlantUML (из строки и файла)
- Получения справки по синтаксису PlantUML
- Просмотра доступных тем оформления

Инструменты MCP:
    generate_code_screenshot
        Создаёт скриншот кода из строки.
    generate_file_screenshot
        Создаёт скриншот кода из файла (⚠️ лимит 200 строк).
    generate_entity_screenshot
        Извлекает и создаёт скриншот конкретной функции/класса/метода (✨ без лимита).
    generate_architecture_diagram
        Генерирует UML диаграмму из PlantUML кода.
    generate_diagram_from_file
        Генерирует UML диаграмму из .puml файла.
    get_plantuml_guide
        Возвращает справку по синтаксису PlantUML.
    list_plantuml_themes
        Возвращает список доступных тем оформления.
"""

import logging
import os

from mcp.server.fastmcp import FastMCP

from src.code_to_image import create_code_screenshot
from src.code_extractor import extract_code_entity, list_entities, EntityNotFoundError
from src.diagram_renderer import (
    JavaNotFoundError,
    PlantUMLRenderError,
    PlantUMLSyntaxError,
    ensure_java_environment,
    render_diagram_from_string,
)
from src.font_manager import list_available_fonts
from src.guide_manager import get_guide, list_guides, list_themes

logger = logging.getLogger(__name__)

MAX_FILE_LINES = 200

mcp = FastMCP("Code Screenshot Tool")


def _generate_screenshot_from_code(
    code: str,
    language: str,
    output_path: str,
    style: str,
    font_size: int,
    scale_factor: int,
    line_numbers: bool,
    font_name: str,
    format: str,
) -> dict:
    """Генерирует скриншот из кода (внутренняя функция)."""
    logger.info(f"📥 Получен запрос generate_code_screenshot")
    logger.debug(f"📝 Параметры: language={language}, style={style}, font={font_name}")

    try:
        if not os.path.isabs(output_path):
            logger.error(f"🚫 Путь не абсолютный: {output_path}")
            return {
                "success": False,
                "error": "Путь должен быть абсолютным",
                "suggestion": f"Используйте абсолютный путь, например: /path/to/{output_path}",
            }

        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            logger.debug(f"🗂️ Создана директория: {output_dir}")

        create_code_screenshot(
            code_string=code,
            language=language,
            output_file=output_path,
            style=style,
            font_size=font_size,
            scale_factor=scale_factor,
            line_numbers=line_numbers,
            font_name=font_name,
            format=format,
        )

        file_size = os.path.getsize(output_path)
        file_size_kb = round(file_size / 1024, 2)

        logger.info(f"📤 Отправлен результат: success=True, size={file_size_kb}KB")

        return {
            "success": True,
            "output_path": output_path,
            "file_size_kb": file_size_kb,
            "format": format,
            "scale_factor": scale_factor,
            "font_used": font_name,
        }

    except Exception as e:
        logger.error(f"❌ Ошибка генерации: {e}")
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Проверьте корректность параметров и доступность шрифта",
            "available_fonts": list_available_fonts(),
        }


@mcp.tool()
def generate_code_screenshot(
    code: str,
    language: str,
    output_path: str,
    detail_level: str = "High",
    image_format: str = "webp",
    style: str = "monokai",
    font_size: int = 18,
    line_numbers: bool = True,
    font_name: str = "JetBrainsMono",
) -> dict:
    """Создаёт скриншот кода из строки.

    Args:
        code: Исходный код для генерации изображения.
        language: Язык программирования (python, typescript, javascript, sql).
        output_path: АБСОЛЮТНЫЙ путь к выходному файлу.
        detail_level: Уровень детализации ('Low', 'Medium', 'High', 'Ultra', 'Extreme').
        image_format: Формат изображения ('webp', 'png', 'jpeg').
        style: Стиль подсветки (monokai, dracula, github-dark, vim).
        font_size: Базовый размер шрифта (умножается на detail_level).
        line_numbers: Показывать нумерацию строк.
        font_name: Имя шрифта (JetBrainsMono, FiraCode, CascadiaCode, Consolas).

    Returns:
        Словарь с информацией о созданном изображении.
    """
    # Конвертируем detail_level в scale_factor через QUALITY_LEVELS
    from src.diagram_renderer import QUALITY_LEVELS

    level_key = detail_level.capitalize()
    scale_factor = QUALITY_LEVELS.get(level_key, 3.0)  # Fallback на High

    return _generate_screenshot_from_code(
        code=code,
        language=language,
        output_path=output_path,
        style=style,
        font_size=font_size,
        scale_factor=scale_factor,
        line_numbers=line_numbers,
        font_name=font_name,
        format=image_format,
    )


@mcp.tool()
def generate_file_screenshot(
    file_path: str,
    output_path: str,
    language: str | None = None,
    detail_level: str = "High",
    image_format: str = "webp",
    style: str = "monokai",
    font_size: int = 18,
    line_numbers: bool = True,
    font_name: str = "JetBrainsMono",
) -> dict:
    """Создаёт скриншот кода из файла.

    ⚠️ ВАЖНО: Файл ограничен 200 строками.

    Args:
        file_path: АБСОЛЮТНЫЙ путь к файлу с исходным кодом.
        output_path: АБСОЛЮТНЫЙ путь к выходному файлу.
        language: Язык программирования (если None - определяется по расширению).
        detail_level: Уровень детализации ('Low', 'Medium', 'High', 'Ultra', 'Extreme').
        image_format: Формат изображения ('webp', 'png', 'jpeg').
        style: Стиль подсветки (monokai, dracula, github-dark, vim).
        font_size: Базовый размер шрифта (умножается на detail_level).
        line_numbers: Показывать нумерацию строк.
        font_name: Имя шрифта (JetBrainsMono, FiraCode, CascadiaCode, Consolas).

    Returns:
        Словарь с информацией о созданном изображении.
    """
    logger.info(f"📥 Получен запрос generate_file_screenshot: {file_path}")

    try:
        if not os.path.isabs(file_path):
            logger.error(f"🚫 Путь к файлу не абсолютный: {file_path}")
            return {
                "success": False,
                "error": "Путь к файлу должен быть абсолютным",
                "suggestion": f"Используйте абсолютный путь, например: /path/to/{file_path}",
            }

        if not os.path.exists(file_path):
            logger.error(f"❌ Файл не найден: {file_path}")
            return {
                "success": False,
                "error": f"Файл не найден: {file_path}",
                "suggestion": "Проверьте правильность пути к файлу",
            }

        if not os.path.isfile(file_path):
            logger.error(f"❌ Путь указывает не на файл: {file_path}")
            return {
                "success": False,
                "error": f"Путь указывает не на файл: {file_path}",
                "suggestion": "Укажите путь к файлу, а не к папке",
            }

        logger.debug(f"📂 Чтение файла: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) > MAX_FILE_LINES:
            logger.warning(
                f"⚠️ Файл содержит {len(lines)} строк, превышает лимит {MAX_FILE_LINES}"
            )
            return {
                "success": False,
                "error": f"Файл содержит {len(lines)} строк, что превышает лимит {MAX_FILE_LINES}",
                "suggestion": "Используйте generate_code_screenshot для фрагмента кода или файл меньшего размера",
                "lines_in_file": len(lines),
                "max_allowed": MAX_FILE_LINES,
            }

        code = "".join(lines)

        if language is None:
            ext_to_lang = {
                ".py": "python",
                ".js": "javascript",
                ".ts": "typescript",
                ".jsx": "jsx",
                ".tsx": "tsx",
                ".java": "java",
                ".c": "c",
                ".cpp": "cpp",
                ".cs": "csharp",
                ".go": "go",
                ".rs": "rust",
                ".rb": "ruby",
                ".php": "php",
                ".swift": "swift",
                ".kt": "kotlin",
                ".scala": "scala",
                ".sql": "sql",
                ".html": "html",
                ".css": "css",
                ".json": "json",
                ".yaml": "yaml",
                ".yml": "yaml",
                ".xml": "xml",
                ".sh": "bash",
                ".bat": "batch",
                ".ps1": "powershell",
                ".md": "markdown",
            }

            _, ext = os.path.splitext(file_path)
            language = ext_to_lang.get(ext.lower(), "text")
            logger.debug(f"🔍 Определён язык по расширению: {language}")

        # Конвертируем detail_level в scale_factor через QUALITY_LEVELS
        from src.diagram_renderer import QUALITY_LEVELS

        level_key = detail_level.capitalize()
        scale_factor = QUALITY_LEVELS.get(level_key, 3.0)  # Fallback на High

        result = _generate_screenshot_from_code(
            code=code,
            language=language,
            output_path=output_path,
            style=style,
            font_size=font_size,
            scale_factor=scale_factor,
            line_numbers=line_numbers,
            font_name=font_name,
            format=image_format,
        )

        if result.get("success"):
            result["source_file"] = file_path
            result["lines_processed"] = len(lines)
            result["language_detected"] = language

        return result

    except UnicodeDecodeError:
        logger.error(f"🌐 Ошибка кодировки файла: {file_path}")
        return {
            "success": False,
            "error": "Не удалось прочитать файл как текст (возможно, это бинарный файл)",
            "suggestion": "Убедитесь, что файл содержит текстовый код",
        }
    except Exception as e:
        logger.error(f"❌ Ошибка обработки файла: {e}")
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Проверьте доступность файла и корректность параметров",
        }


@mcp.tool()
def generate_entity_screenshot(
    file_path: str,
    entity_name: str,
    output_path: str,
    include_decorators: bool = True,
    detail_level: str = "High",
    image_format: str = "webp",
    style: str = "monokai",
    font_size: int = 18,
    line_numbers: bool = True,
    font_name: str = "JetBrainsMono",
) -> dict:
    """Извлекает и создаёт скриншот конкретной функции/класса/метода из Python файла.

    ✨ УМНЫЙ ИНСТРУМЕНТ для точечной работы с большими файлами без ограничения на размер.
    Использует AST (Abstract Syntax Tree) для хирургического извлечения кода.

    Use this to extract specific functions or classes from large files without reading
    the whole file into context. Supports format 'ClassName.method_name' for methods.

    Args:
        file_path: АБСОЛЮТНЫЙ путь к Python файлу.
        entity_name: Имя сущности для извлечения:
            - "function_name" для функции
            - "ClassName" для класса целиком
            - "ClassName.method_name" для метода класса
        output_path: АБСОЛЮТНЫЙ путь к выходному файлу.
        include_decorators: Включать декораторы (@tool, @pytest.fixture, etc) в скриншот.
        detail_level: Уровень детализации ('Low', 'Medium', 'High', 'Ultra', 'Extreme').
        image_format: Формат изображения ('webp', 'png', 'jpeg').
        style: Стиль подсветки (monokai, dracula, github-dark, vim).
        font_size: Базовый размер шрифта (умножается на detail_level).
        line_numbers: Показывать нумерацию строк.
        font_name: Имя шрифта (JetBrainsMono, FiraCode, CascadiaCode, Consolas).

    Returns:
        Словарь с информацией о созданном изображении и метаданными сущности.
    """
    logger.info(
        f"📥 Получен запрос generate_entity_screenshot: {entity_name} из {file_path}"
    )

    try:
        # Извлекаем код сущности через AST
        extracted_code = extract_code_entity(
            file_path=file_path,
            entity_name=entity_name,
            include_decorators=include_decorators,
        )

        logger.debug(f"✅ Извлечено {len(extracted_code)} символов кода")

        # Конвертируем detail_level в scale_factor через QUALITY_LEVELS
        from src.diagram_renderer import QUALITY_LEVELS

        level_key = detail_level.capitalize()
        scale_factor = QUALITY_LEVELS.get(level_key, 3.0)  # Fallback на High

        # Генерируем скриншот извлечённого кода
        result = _generate_screenshot_from_code(
            code=extracted_code,
            language="python",  # Всегда Python для этого инструмента
            output_path=output_path,
            style=style,
            font_size=font_size,
            scale_factor=scale_factor,
            line_numbers=line_numbers,
            font_name=font_name,
            format=image_format,
        )

        # Добавляем метаданные об извлечении
        if result.get("success"):
            result["entity_extracted"] = entity_name
            result["source_file"] = file_path
            result["decorators_included"] = include_decorators
            result["extraction_method"] = "AST"

        return result

    except EntityNotFoundError as e:
        logger.error(f"🔍 Сущность не найдена: {e}")
        # Пытаемся показать список доступных сущностей для помощи
        try:
            entities = list_entities(file_path)
            return {
                "success": False,
                "error": str(e),
                "suggestion": (
                    "Проверьте правильность имени сущности. "
                    "Для методов используйте формат 'ClassName.method_name'"
                ),
                "available_entities": entities,
            }
        except Exception:
            return {
                "success": False,
                "error": str(e),
                "suggestion": "Проверьте правильность имени сущности и структуру файла",
            }

    except FileNotFoundError:
        logger.error(f"❌ Файл не найден: {file_path}")
        return {
            "success": False,
            "error": f"Файл не найден: {file_path}",
            "suggestion": "Проверьте правильность пути к файлу",
        }

    except SyntaxError as e:
        logger.error(f"💥 Синтаксическая ошибка в Python файле: {e}")
        return {
            "success": False,
            "error": "Синтаксическая ошибка в Python файле",
            "details": str(e),
            "suggestion": "Исправьте синтаксические ошибки в исходном файле",
        }

    except Exception as e:
        logger.error(f"❌ Ошибка извлечения сущности: {e}")
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Проверьте структуру файла и корректность параметров",
        }


@mcp.tool()
def generate_architecture_diagram(
    diagram_code: str,
    output_path: str,
    detail_level: str = "High",
    image_format: str = "png",
    theme_name: str = "default",
) -> dict:
    """Генерирует UML диаграмму из PlantUML кода.

    ⚠️ ВАЖНО: Требуется Java (JRE 8+).

    Args:
        diagram_code: PlantUML код диаграммы.
        output_path: АБСОЛЮТНЫЙ путь к выходному файлу.
        detail_level: Уровень детализации ('Low', 'Medium', 'High', 'Ultra', 'Extreme').
        image_format: Формат изображения ('png', 'svg', 'eps', 'pdf', 'webp').
        theme_name: Имя темы оформления (default или None).

    Returns:
        Словарь с информацией о созданной диаграмме.
    """
    logger.info("📥 Получен запрос generate_architecture_diagram")

    try:
        if not os.path.isabs(output_path):
            logger.error(f"🚫 Путь не абсолютный: {output_path}")
            return {
                "success": False,
                "error": "Путь должен быть абсолютным",
                "suggestion": f"Используйте абсолютный путь, например: /path/to/{output_path}",
            }

        try:
            ensure_java_environment()
        except JavaNotFoundError as e:
            logger.error("☕ Java не найдена в системе")
            return {
                "success": False,
                "error": "Java не найдена в системе",
                "details": str(e),
                "suggestion": "Установите JRE (Java Runtime Environment) версии 8 или выше",
                "install_instructions": {
                    "macOS": "brew install openjdk",
                    "Windows": "https://adoptium.net/",
                    "Linux": "sudo apt-get install default-jre",
                },
            }

        # Конвертируем detail_level в scale_factor через QUALITY_LEVELS
        from src.diagram_renderer import QUALITY_LEVELS

        level_key = detail_level.capitalize()
        scale_factor = QUALITY_LEVELS.get(level_key, 3.0)  # Fallback на High

        result = render_diagram_from_string(
            diagram_code=diagram_code,
            output_path=output_path,
            format=image_format,
            theme_name=theme_name,
            scale_factor=scale_factor,
        )

        logger.info(f"📤 Отправлен результат: success={result.get('success')}")
        return result

    except PlantUMLSyntaxError as e:
        logger.error(f"💥 Синтаксическая ошибка PlantUML: {e}")
        return {
            "success": False,
            "error": "Синтаксическая ошибка в PlantUML коде",
            "details": str(e),
            "suggestion": (
                "Проверьте правильность синтаксиса PlantUML. "
                "ПОДСКАЗКА: Вызовите инструмент get_plantuml_guide с нужным типом диаграммы "
                "(class, sequence, component, activity) для получения справки по синтаксису "
                "и стереотипам (<<Core>>, <<Adapter>>, <<Infrastructure>>)."
            ),
        }
    except PlantUMLRenderError as e:
        logger.error(f"❌ Ошибка рендеринга PlantUML: {e}")
        return {
            "success": False,
            "error": "Ошибка рендеринга PlantUML диаграммы",
            "details": str(e),
            "suggestion": (
                "Проверьте синтаксис PlantUML кода. "
                "ПОДСКАЗКА: Вызовите инструмент get_plantuml_guide с нужным типом диаграммы "
                "(class, sequence, component, activity) для получения справки по правильному синтаксису."
            ),
        }
    except FileNotFoundError as e:
        logger.error(f"❌ Файл не найден: {e}")
        return {
            "success": False,
            "error": "Файл или ресурс не найден",
            "details": str(e),
            "suggestion": "Проверьте наличие PlantUML JAR файла и темы оформления",
        }
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Проверьте корректность параметров и доступность ресурсов",
        }


@mcp.tool()
def generate_diagram_from_file(
    file_path: str,
    output_path: str,
    detail_level: str = "High",
    image_format: str = "png",
    theme_name: str = "default",
) -> dict:
    """Генерирует UML диаграмму из сохранённого .puml файла.

    Use this when PlantUML diagram code is already saved in a file. This is the preferred
    way for complex diagrams to avoid generation errors and save tokens.

    ⚠️ ВАЖНО: Требуется Java (JRE 8+).

    Args:
        file_path: АБСОЛЮТНЫЙ путь к .puml файлу с PlantUML кодом.
        output_path: АБСОЛЮТНЫЙ путь к выходному файлу изображения.
        detail_level: Уровень детализации ('Low', 'Medium', 'High', 'Ultra', 'Extreme').
        image_format: Формат изображения ('png', 'svg', 'eps', 'pdf', 'webp').
        theme_name: Имя темы оформления (default или None).

    Returns:
        Словарь с информацией о созданной диаграмме.
    """
    logger.info(f"📥 Получен запрос generate_diagram_from_file: {file_path}")

    try:
        # Проверка существования файла
        if not os.path.isabs(file_path):
            logger.error(f"🚫 Путь к файлу не абсолютный: {file_path}")
            return {
                "success": False,
                "error": "Путь к файлу должен быть абсолютным",
                "suggestion": f"Используйте абсолютный путь, например: /path/to/{file_path}",
            }

        if not os.path.exists(file_path):
            logger.error(f"❌ Файл не найден: {file_path}")
            return {
                "success": False,
                "error": f"Файл не найден: {file_path}",
                "suggestion": "Проверьте правильность пути к .puml файлу",
            }

        # Чтение PlantUML кода из файла
        logger.debug(f"📂 Чтение PlantUML файла: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            diagram_code = f.read()

        logger.debug(f"📝 Прочитано {len(diagram_code)} символов PlantUML кода")

        # Проверка Java окружения
        try:
            ensure_java_environment()
        except JavaNotFoundError as e:
            logger.error("☕ Java не найдена в системе")
            return {
                "success": False,
                "error": "Java не найдена в системе",
                "details": str(e),
                "suggestion": "Установите JRE (Java Runtime Environment) версии 8 или выше",
                "install_instructions": {
                    "macOS": "brew install openjdk",
                    "Windows": "https://adoptium.net/",
                    "Linux": "sudo apt-get install default-jre",
                },
            }

        # Конвертируем detail_level в scale_factor через QUALITY_LEVELS
        from src.diagram_renderer import QUALITY_LEVELS

        level_key = detail_level.capitalize()
        scale_factor = QUALITY_LEVELS.get(level_key, 3.0)  # Fallback на High

        # Генерируем диаграмму
        result = render_diagram_from_string(
            diagram_code=diagram_code,
            output_path=output_path,
            format=image_format,
            theme_name=theme_name,
            scale_factor=scale_factor,
        )

        # Добавляем метаданные об источнике
        if result.get("success"):
            result["source_file"] = file_path
            result["code_length"] = len(diagram_code)

        logger.info(f"📤 Отправлен результат: success={result.get('success')}")
        return result

    except UnicodeDecodeError:
        logger.error(f"🌐 Ошибка кодировки файла: {file_path}")
        return {
            "success": False,
            "error": "Не удалось прочитать файл как текст",
            "suggestion": "Убедитесь, что .puml файл сохранён в UTF-8 кодировке",
        }

    except PlantUMLSyntaxError as e:
        logger.error(f"💥 Синтаксическая ошибка PlantUML: {e}")
        return {
            "success": False,
            "error": "Синтаксическая ошибка в PlantUML коде",
            "details": str(e),
            "source_file": file_path,
            "suggestion": (
                "Проверьте синтаксис PlantUML в файле. "
                "ПОДСКАЗКА: Вызовите инструмент get_plantuml_guide с нужным типом диаграммы "
                "для получения справки."
            ),
        }

    except PlantUMLRenderError as e:
        logger.error(f"❌ Ошибка рендеринга PlantUML: {e}")
        return {
            "success": False,
            "error": "Ошибка рендеринга PlantUML диаграммы",
            "details": str(e),
            "source_file": file_path,
            "suggestion": "Проверьте синтаксис PlantUML кода в файле",
        }

    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Проверьте корректность .puml файла и доступность ресурсов",
        }


@mcp.tool()
def get_plantuml_guide(
    diagram_type: str,
    detail_level: str = "brief",
) -> dict:
    """Возвращает справку по синтаксису PlantUML для указанного типа диаграммы.

    Используйте этот инструмент, если не уверены в синтаксисе или получили ошибку
    при генерации диаграммы.

    Args:
        diagram_type: Тип диаграммы (class, sequence, component, activity, themes).
        detail_level: Уровень детализации ('brief' — краткая выжимка, 'detailed' — полная версия).

    Returns:
        Словарь с содержимым гайда и списком доступных тем.
    """
    logger.info(f"📚 Запрос гайда PlantUML: type={diagram_type}, level={detail_level}")

    full = detail_level.lower() == "detailed"
    guide_content = get_guide(diagram_type, full=full)

    available_guides = list_guides()
    available_guide_types = [g["type"] for g in available_guides]

    return {
        "success": True,
        "diagram_type": diagram_type,
        "detail_level": detail_level,
        "content": guide_content,
        "available_guides": available_guide_types,
        "hint": "Используйте стереотипы <<Adapter>>, <<Core>>, <<Infrastructure>> для архитектурных диаграмм.",
    }


@mcp.tool()
def list_plantuml_themes() -> dict:
    """Возвращает список доступных тем оформления для PlantUML диаграмм.

    Returns:
        Словарь со списком тем и рекомендациями по выбору.
    """
    logger.info("🎨 Запрос списка тем PlantUML")

    themes = list_themes()

    return {
        "success": True,
        "themes": themes,
        "recommendation": (
            "Используйте 'dark_gold' для презентаций, "
            "'light_fresh' для печатной документации, "
            "'default' для общего использования."
        ),
        "stereotypes_hint": (
            "Во всех темах поддерживаются стереотипы: "
            "<<Adapter>> (входные точки), "
            "<<Core>> (бизнес-логика), "
            "<<Infrastructure>> (инфраструктура)."
        ),
    }


if __name__ == "__main__":
    mcp.run()
