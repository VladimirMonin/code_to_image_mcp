#!/usr/bin/env python3
"""MCP сервер для генерации скриншотов кода и диаграмм.

Предоставляет инструменты для:
- Генерации скриншотов кода из строки и файла
- Генерации UML диаграмм через PlantUML

Инструменты MCP:
    generate_code_screenshot
        Создаёт скриншот кода из строки.
    generate_file_screenshot
        Создаёт скриншот кода из файла.
    generate_architecture_diagram
        Генерирует UML диаграмму из PlantUML кода.
"""

import logging
import os

from mcp.server.fastmcp import FastMCP

from code_to_image import create_code_screenshot
from diagram_renderer import (
    JavaNotFoundError,
    PlantUMLRenderError,
    PlantUMLSyntaxError,
    ensure_java_environment,
    render_diagram_from_string,
)
from font_manager import list_available_fonts

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
    style: str = "monokai",
    font_size: int = 18,
    scale_factor: int = 3,
    line_numbers: bool = True,
    font_name: str = "JetBrainsMono",
    format: str = "WEBP",
) -> dict:
    """Создаёт скриншот кода из строки.

    Args:
        code: Исходный код для генерации изображения.
        language: Язык программирования (python, typescript, javascript, sql).
        output_path: АБСОЛЮТНЫЙ путь к выходному файлу.
        style: Стиль подсветки (monokai, dracula, github-dark, vim).
        font_size: Базовый размер шрифта (умножается на scale_factor).
        scale_factor: Фактор масштабирования (3-5 рекомендуется).
        line_numbers: Показывать нумерацию строк.
        font_name: Имя шрифта (JetBrainsMono, FiraCode, CascadiaCode, Consolas).
        format: Формат изображения (WEBP, PNG, JPEG).

    Returns:
        Словарь с информацией о созданном изображении.
    """
    return _generate_screenshot_from_code(
        code=code,
        language=language,
        output_path=output_path,
        style=style,
        font_size=font_size,
        scale_factor=scale_factor,
        line_numbers=line_numbers,
        font_name=font_name,
        format=format,
    )


@mcp.tool()
def generate_file_screenshot(
    file_path: str,
    output_path: str,
    language: str | None = None,
    style: str = "monokai",
    font_size: int = 18,
    scale_factor: int = 3,
    line_numbers: bool = True,
    font_name: str = "JetBrainsMono",
    format: str = "WEBP",
) -> dict:
    """Создаёт скриншот кода из файла.

    ⚠️ ВАЖНО: Файл ограничен 200 строками.

    Args:
        file_path: АБСОЛЮТНЫЙ путь к файлу с исходным кодом.
        output_path: АБСОЛЮТНЫЙ путь к выходному файлу.
        language: Язык программирования (если None - определяется по расширению).
        style: Стиль подсветки (monokai, dracula, github-dark, vim).
        font_size: Базовый размер шрифта (умножается на scale_factor).
        scale_factor: Фактор масштабирования (3-5 рекомендуется).
        line_numbers: Показывать нумерацию строк.
        font_name: Имя шрифта (JetBrainsMono, FiraCode, CascadiaCode, Consolas).
        format: Формат изображения (WEBP, PNG, JPEG).

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

        result = _generate_screenshot_from_code(
            code=code,
            language=language,
            output_path=output_path,
            style=style,
            font_size=font_size,
            scale_factor=scale_factor,
            line_numbers=line_numbers,
            font_name=font_name,
            format=format,
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
def generate_architecture_diagram(
    diagram_code: str,
    output_path: str,
    format: str = "png",
    theme_name: str = "default",
) -> dict:
    """Генерирует UML диаграмму из PlantUML кода.

    ⚠️ ВАЖНО: Требуется Java (JRE 8+).

    Args:
        diagram_code: PlantUML код диаграммы.
        output_path: АБСОЛЮТНЫЙ путь к выходному файлу.
        format: Формат изображения (png, svg, eps, pdf).
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

        result = render_diagram_from_string(
            diagram_code=diagram_code,
            output_path=output_path,
            format=format,
            theme_name=theme_name,
        )

        logger.info(f"📤 Отправлен результат: success={result.get('success')}")
        return result

    except PlantUMLSyntaxError as e:
        logger.error(f"💥 Синтаксическая ошибка PlantUML: {e}")
        return {
            "success": False,
            "error": "Синтаксическая ошибка в PlantUML коде",
            "details": str(e),
            "suggestion": "Проверьте правильность синтаксиса PlantUML.",
        }
    except PlantUMLRenderError as e:
        logger.error(f"❌ Ошибка рендеринга PlantUML: {e}")
        return {
            "success": False,
            "error": "Ошибка рендеринга PlantUML диаграммы",
            "details": str(e),
            "suggestion": "Проверьте синтаксис PlantUML кода.",
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


if __name__ == "__main__":
    mcp.run()
