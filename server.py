#!/usr/bin/env python3
"""MCP сервер для генерации скриншотов кода."""

from mcp.server.fastmcp import FastMCP
from code_to_image import create_code_screenshot
from font_manager import list_available_fonts
import os

# Константы
MAX_FILE_LINES = 200  # Максимальное количество строк для чтения из файла

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
    """Внутренняя функция для генерации скриншота.

    DRY: Единая точка генерации для обоих инструментов.
    """
    try:
        # Проверка абсолютного пути
        if not os.path.isabs(output_path):
            return {
                "success": False,
                "error": "Путь должен быть абсолютным",
                "suggestion": f"Используйте абсолютный путь, например: C:/Users/user/{output_path}",
            }

        # Создаем директорию если не существует
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Вызываем функцию генерации
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

        # Получаем размер файла
        file_size = os.path.getsize(output_path)

        return {
            "success": True,
            "output_path": output_path,
            "file_size_kb": round(file_size / 1024, 2),
            "format": format,
            "scale_factor": scale_factor,
            "font_used": font_name,
        }

    except Exception as e:
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
    """Создать высококачественный скриншот кода из строки.

    Args:
        code: Исходный код для генерации изображения
        language: Язык программирования (python, typescript, javascript, sql, etc.)
        output_path: АБСОЛЮТНЫЙ путь к выходному файлу (например: C:/Users/user/image.webp)
        style: Стиль подсветки (monokai, dracula, github-dark, vim, etc.)
        font_size: Базовый размер шрифта (будет умножен на scale_factor)
        scale_factor: Фактор масштабирования для качества (3-5 рекомендуется)
        line_numbers: Показывать нумерацию строк
        font_name: Имя шрифта (JetBrainsMono, FiraCode, CascadiaCode, Consolas)
        format: Формат изображения (WEBP, PNG, JPEG)

    Returns:
        Словарь с информацией о созданном изображении или ошибке

    Example:
        generate_code_screenshot(
            code="print('Hello')",
            language="python",
            output_path="C:/Users/user/screenshot.webp"
        )
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
    """Создать высококачественный скриншот кода из файла.

    ⚠️ ВАЖНО: Файл будет прочитан целиком, но ограничен максимум 200 строками.
    Для больших файлов используйте generate_code_screenshot с нужным фрагментом кода.

    Args:
        file_path: АБСОЛЮТНЫЙ путь к файлу с исходным кодом
        output_path: АБСОЛЮТНЫЙ путь к выходному файлу (например: C:/Users/user/image.webp)
        language: Язык программирования (python, typescript, etc.). Если None - определяется по расширению
        style: Стиль подсветки (monokai, dracula, github-dark, vim, etc.)
        font_size: Базовый размер шрифта (будет умножен на scale_factor)
        scale_factor: Фактор масштабирования для качества (3-5 рекомендуется)
        line_numbers: Показывать нумерацию строк
        font_name: Имя шрифта (JetBrainsMono, FiraCode, CascadiaCode, Consolas)
        format: Формат изображения (WEBP, PNG, JPEG)

    Returns:
        Словарь с информацией о созданном изображении или ошибке

    Example:
        generate_file_screenshot(
            file_path="C:/Users/user/script.py",
            output_path="C:/Users/user/screenshot.webp"
        )
    """
    try:
        # Проверка существования файла
        if not os.path.isabs(file_path):
            return {
                "success": False,
                "error": "Путь к файлу должен быть абсолютным",
                "suggestion": f"Используйте абсолютный путь, например: C:/Users/user/{file_path}",
            }

        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"Файл не найден: {file_path}",
                "suggestion": "Проверьте правильность пути к файлу",
            }

        if not os.path.isfile(file_path):
            return {
                "success": False,
                "error": f"Путь указывает не на файл: {file_path}",
                "suggestion": "Укажите путь к файлу, а не к папке",
            }

        # Читаем файл
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Проверяем лимит строк
        if len(lines) > MAX_FILE_LINES:
            return {
                "success": False,
                "error": f"Файл содержит {len(lines)} строк, что превышает лимит {MAX_FILE_LINES}",
                "suggestion": "Используйте generate_code_screenshot для фрагмента кода или файл меньшего размера",
                "lines_in_file": len(lines),
                "max_allowed": MAX_FILE_LINES,
            }

        code = "".join(lines)

        # Определяем язык по расширению, если не указан
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

        # Используем общую функцию генерации
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

        # Добавляем информацию о файле
        if result.get("success"):
            result["source_file"] = file_path
            result["lines_processed"] = len(lines)
            result["language_detected"] = language

        return result

    except UnicodeDecodeError:
        return {
            "success": False,
            "error": "Не удалось прочитать файл как текст (возможно, это бинарный файл)",
            "suggestion": "Убедитесь, что файл содержит текстовый код",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Проверьте доступность файла и корректность параметров",
        }


if __name__ == "__main__":
    mcp.run()
