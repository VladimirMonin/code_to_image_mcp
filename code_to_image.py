#!/usr/bin/env python3
"""Генератор скриншотов исходного кода.

Модуль создаёт высококачественные изображения из исходного кода
с использованием Pygments для подсветки синтаксиса и Pillow для обработки.

Функции:
    create_code_image(code_string, language, **options) -> Image
        Создаёт изображение фрагмента кода и возвращает PIL Image.
    create_code_screenshot(code_string, language, output_file, **options) -> dict
        LEGACY: генерирует изображение и сохраняет в файл.
"""

import io
import logging
from pathlib import Path
from typing import Literal

import pygments
from PIL import Image
from pygments.formatters import ImageFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

from font_manager import get_font_path
from image_utils import save_image

logger = logging.getLogger(__name__)

ImageFormat = Literal["png", "jpeg", "webp"]


def create_code_image(
    code_string: str,
    language: str,
    style: str = "monokai",
    font_name: str = "JetBrainsMono",
    font_size: int = 18,
    pad: int = 25,
    scale_factor: float = 3.0,
    transparent: bool = False,
    line_numbers: bool = True,
    line_pad: int = 10,
    line_number_bg: str | None = None,
    line_number_fg: str = "#888888",
) -> Image.Image:
    """Создаёт изображение фрагмента кода и возвращает PIL Image объект.

    Args:
        code_string: Строка с исходным кодом.
        language: Язык программирования (для лексера Pygments).
        style: Название стиля Pygments (по умолчанию 'monokai').
        font_name: Имя шрифта (по умолчанию 'JetBrainsMono').
        font_size: Размер шрифта (по умолчанию 18).
        pad: Отступ вокруг кода в пикселях (по умолчанию 25).
        scale_factor: Коэффициент масштабирования для высокого DPI (1.0-5.0).
        transparent: Прозрачный фон (по умолчанию False).
        line_numbers: Показывать номера строк (по умолчанию True).
        line_pad: Отступ между номерами строк и кодом (по умолчанию 10).
        line_number_bg: Цвет фона номеров строк (по умолчанию из стиля).
        line_number_fg: Цвет текста номеров строк (по умолчанию '#888888').

    Returns:
        PIL Image объект с отрендеренным кодом.

    Raises:
        ValueError: Если язык не поддерживается (используется fallback 'text').
    """
    logger.info(f"🎨 Генерация изображения кода для языка: {language}")

    # Получаем лексер для языка программирования
    try:
        lexer = get_lexer_by_name(language, stripall=True)
    except pygments.util.ClassNotFound:
        logger.warning(
            f"🎯 Лексер для языка '{language}' не найден, используется 'text'"
        )
        lexer = get_lexer_by_name("text", stripall=True)

    # Загружаем стиль Pygments
    style_inst = get_style_by_name(style)
    logger.debug(f"🎭 Применён стиль: {style}")

    # Настройка прозрачности
    if transparent:
        style_inst.background_color = None
        logger.debug("🔍 Применена прозрачность фона")

    # Применяем масштабирование к размерам
    logger.debug(f"🖼️ Масштабирование: {scale_factor}x")
    scaled_font_size = int(font_size * scale_factor)
    scaled_pad = int(pad * scale_factor)
    scaled_line_pad = int(line_pad * scale_factor)

    # Получаем путь к шрифту
    try:
        font_path = get_font_path(font_name)
        logger.info(f"📦 Загружен шрифт: {font_path}")
    except (ValueError, FileNotFoundError) as e:
        logger.warning(f"🎯 {e}, используется fallback: Consolas")
        font_path = "Consolas"

    # Фон номеров строк
    if line_number_bg is None:
        line_number_bg = style_inst.background_color

    logger.debug(
        f"🔧 Параметры форматтера: font_size={scaled_font_size}, "
        f"line_numbers={line_numbers}, pad={scaled_pad}"
    )

    # Создаём форматтер для генерации изображения
    formatter = ImageFormatter(
        style=style_inst,
        full=True,
        font_name=font_path,
        font_size=scaled_font_size,
        image_pad=scaled_pad,
        line_numbers=line_numbers,
        line_pad=scaled_line_pad,
        line_number_bg=line_number_bg,
        line_number_fg=line_number_fg,
        image_format="PNG",  # Pygments всегда генерирует PNG
    )

    try:
        # Генерируем байты изображения
        image_bytes = pygments.highlight(code_string, lexer, formatter, outfile=None)
        img = Image.open(io.BytesIO(image_bytes))

        logger.info(
            f"✅ Изображение сгенерировано: {img.width}x{img.height}px, "
            f"масштаб: {scale_factor}x"
        )

        return img

    except Exception as e:
        logger.error(f"❌ Ошибка при генерации: {e}")
        raise


def create_code_screenshot(
    code_string: str, language: str, output_file: str | Path, **options
) -> dict:
    """Создаёт скриншот фрагмента кода и сохраняет в файл.

    LEGACY функция для обратной совместимости. Использует create_code_image()
    и image_utils для сохранения.

    Args:
        code_string: Строка с исходным кодом.
        language: Язык программирования (для лексера Pygments).
        output_file: Путь к выходному файлу изображения.
        **options: Дополнительные параметры:
            - style: Название стиля Pygments (по умолчанию 'monokai').
            - font_name: Имя шрифта (по умолчанию 'JetBrainsMono').
            - font_size: Размер шрифта (по умолчанию 18).
            - pad: Отступ вокруг кода (по умолчанию 25).
            - format: Формат изображения (png, jpeg, webp; по умолчанию 'webp').
            - scale_factor: Фактор масштабирования (по умолчанию 3.0).
            - transparent: Прозрачный фон (по умолчанию False).
            - line_numbers: Нумерация строк (по умолчанию True).
            - line_pad: Отступ между номерами и кодом (по умолчанию 10).
            - line_number_bg: Цвет фона номеров (по умолчанию из стиля).
            - line_number_fg: Цвет текста номеров (по умолчанию '#888888').
            - quality: Качество для JPEG/WEBP (по умолчанию 95).
            - optimize: Оптимизация для PNG (по умолчанию True).

    Returns:
        Словарь с информацией о результате сохранения.

    Raises:
        ValueError: Если язык не поддерживается (используется fallback 'text').
    """
    # Извлекаем параметры
    style = options.get("style", "monokai")
    font_name = options.get("font_name", "JetBrainsMono")
    font_size = options.get("font_size", 18)
    pad = options.get("pad", 25)
    scale_factor = options.get("scale_factor", 3.0)
    transparent = options.get("transparent", False)
    line_numbers = options.get("line_numbers", True)
    line_pad = options.get("line_pad", 10)
    line_number_bg = options.get("line_number_bg", None)
    line_number_fg = options.get("line_number_fg", "#888888")

    # Генерируем изображение через новую функцию
    img = create_code_image(
        code_string=code_string,
        language=language,
        style=style,
        font_name=font_name,
        font_size=font_size,
        pad=pad,
        scale_factor=scale_factor,
        transparent=transparent,
        line_numbers=line_numbers,
        line_pad=line_pad,
        line_number_bg=line_number_bg,
        line_number_fg=line_number_fg,
    )

    # Определяем формат для сохранения
    output_path = Path(output_file)
    save_format = options.get("format", "webp").lower()

    # Если формат не совместим с прозрачностью, меняем на PNG
    if transparent and save_format not in ("png", "webp"):
        logger.warning(
            "⚠️ Прозрачность поддерживается только в PNG и WEBP, переключено на PNG"
        )
        save_format = "png"

    # Сохраняем через image_utils
    save_result = save_image(
        image=img,
        output_path=output_path,
        format=save_format,  # type: ignore
        quality=options.get("quality", 95),
    )

    return {
        "success": True,
        "output_path": save_result["path"],
        "format": save_result["format"],
        "file_size_kb": round(save_result["size_bytes"] / 1024, 2),
        "dimensions": save_result["dimensions"],
        "scale_factor": scale_factor,
        "language": language,
        "style": style,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("=== Code Screenshot Generator Test ===")

    SAMPLE_CODE_TS = """
import React, { useState } from 'react';

interface UserProfile {
  username: string;
  age: number;
}

const Profile: React.FC<UserProfile> = ({ username, age }) => {
  return <div>User: {username}, Age: {age}</div>;
};
"""

    ts_options = {
        "style": "dracula",
        "font_name": "JetBrainsMono",
        "font_size": 18,
        "pad": 10,
        "format": "webp",
        "scale_factor": 3.0,
        "line_numbers": True,
        "line_pad": 5,
        "line_number_fg": "#6272A4",
        "quality": 90,
    }

    print("\nТест 1: TypeScript код (WebP, 3x scale)...")
    result1 = create_code_screenshot(
        code_string=SAMPLE_CODE_TS.strip(),
        language="typescript",
        output_file="tests/output/typescript_screenshot_styled.webp",
        **ts_options,
    )

    print(f"✓ Скриншот создан: {result1['output_path']}")
    print(f"  Размер: {result1['file_size_kb']} KB")
    print(f"  Формат: {result1['format']}")
    print(f"  Разрешение: {result1['dimensions']}")
    print(f"  Масштаб: {result1['scale_factor']}x")

    SAMPLE_CODE_SQL = """
SELECT
    u.id AS user_id,
    u.username,
    u.email
FROM
    users u
INNER JOIN
    orders o ON u.id = o.user_id
WHERE
    u.registration_date > '2023-01-01'
ORDER BY
    u.username;
"""

    sql_options = {
        "style": "github-dark",
        "font_name": "FiraCode",
        "font_size": 20,
        "pad": 40,
        "format": "png",
        "scale_factor": 2.0,
        "line_numbers": False,
        "optimize": True,
    }

    print("\nТест 2: SQL код (PNG, 2x scale, без номеров строк)...")
    result2 = create_code_screenshot(
        code_string=SAMPLE_CODE_SQL.strip(),
        language="sql",
        output_file="tests/output/sql_screenshot_no_lines.png",
        **sql_options,
    )

    print(f"✓ Скриншот создан: {result2['output_path']}")
    print(f"  Размер: {result2['file_size_kb']} KB")
    print(f"  Формат: {result2['format']}")
    print(f"  Разрешение: {result2['dimensions']}")
    print(f"  Масштаб: {result2['scale_factor']}x")
