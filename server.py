#!/usr/bin/env python3
"""MCP сервер для генерации скриншотов кода."""

from mcp.server.fastmcp import FastMCP
from code_to_image import create_code_screenshot
import os

mcp = FastMCP("Code Screenshot Tool")


@mcp.tool()
def generate_code_screenshot(
    code: str,
    language: str,
    output_path: str,
    style: str = "monokai",
    font_size: int = 18,
    scale_factor: int = 3,
    line_numbers: bool = True,
    font_name: str = "Consolas",
    format: str = "WEBP",
) -> dict:
    """Создать высококачественный скриншот кода.

    Args:
        code: Исходный код для генерации изображения
        language: Язык программирования (python, typescript, javascript, sql, etc.)
        output_path: АБСОЛЮТНЫЙ путь к выходному файлу (например: C:/Users/user/image.webp)
        style: Стиль подсветки (monokai, dracula, github-dark, vim, etc.)
        font_size: Базовый размер шрифта (будет умножен на scale_factor)
        scale_factor: Фактор масштабирования для качества (3-5 рекомендуется)
        line_numbers: Показывать нумерацию строк
        font_name: Имя системного шрифта (Consolas, Courier New, Monaco, etc.)
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
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Проверьте доступность шрифта в системе и корректность параметров",
        }


if __name__ == "__main__":
    mcp.run()
