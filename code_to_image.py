#!/usr/bin/env python3
"""Генератор скриншотов исходного кода.

Модуль создаёт высококачественные изображения из исходного кода
с использованием Pygments для подсветки синтаксиса и Pillow для обработки.

Функции:
    create_code_screenshot(code_string, language, output_file, **options) -> None
        Создаёт скриншот фрагмента кода.
"""

import io
import logging

import pygments
from PIL import Image
from pygments.formatters import ImageFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

from font_manager import get_font_path

logger = logging.getLogger(__name__)


def create_code_screenshot(code_string: str, language: str, output_file: str, **options) -> None:
    """Создаёт скриншот фрагмента кода и сохраняет его в файл.

    Args:
        code_string: Строка с исходным кодом.
        language: Язык программирования (для лексера Pygments).
        output_file: Путь к выходному файлу изображения.
        **options: Дополнительные параметры:
            - style: Название стиля Pygments (по умолчанию 'monokai').
            - font_name: Имя шрифта (по умолчанию 'JetBrainsMono').
            - font_size: Размер шрифта (по умолчанию 18).
            - pad: Отступ вокруг кода (по умолчанию 25).
            - format: Формат изображения (PNG, JPEG, WEBP; по умолчанию 'WEBP').
            - scale_factor: Фактор масштабирования (по умолчанию 3).
            - transparent: Прозрачный фон (по умолчанию False).
            - line_numbers: Нумерация строк (по умолчанию True).
            - line_pad: Отступ между номерами и кодом (по умолчанию 10).
            - line_number_bg: Цвет фона номеров (по умолчанию из стиля).
            - line_number_fg: Цвет текста номеров (по умолчанию '#888888').
            - quality: Качество для JPEG/WEBP (по умолчанию 95).
            - optimize: Оптимизация для PNG (по умолчанию True).

    Raises:
        ValueError: Если язык не поддерживается (используется fallback 'text').
    """
    logger.info(f"🎨 Генерация скриншота для языка: {language}")

    try:
        lexer = get_lexer_by_name(language, stripall=True)
    except pygments.util.ClassNotFound:
        logger.warning(f"🎯 Лексер для языка '{language}' не найден, используется 'text'")
        lexer = get_lexer_by_name("text", stripall=True)

    style_name = options.get("style", "monokai")
    style_inst = get_style_by_name(style_name)
    logger.debug(f"🎭 Применён стиль: {style_name}")

    transparent = options.get("transparent", False)
    image_format = options.get("format", "WEBP").upper()

    if transparent:
        style_inst.background_color = None
        if image_format not in ("PNG", "WEBP"):
            logger.warning("⚠️ Прозрачность поддерживается только в PNG и WEBP")
            image_format = "PNG"

    scale = options.get("scale_factor", 3)
    logger.debug(f"🖼️ Масштабирование: {scale}x")

    font_name_input = options.get("font_name", "JetBrainsMono")

    try:
        font_path = get_font_path(font_name_input)
        logger.info(f"📦 Загружен шрифт: {font_path}")
    except (ValueError, FileNotFoundError) as e:
        logger.warning(f"🎯 {e}, используется fallback: Consolas")
        font_path = "Consolas"

    font_size = options.get("font_size", 18) * scale

    line_numbers = options.get("line_numbers", True)
    line_pad = options.get("line_pad", 10) * scale
    line_number_bg = options.get("line_number_bg", style_inst.background_color)
    line_number_fg = options.get("line_number_fg", "#888888")

    pad = options.get("pad", 25) * scale

    logger.debug(f"🔧 Параметры форматтера: font_size={font_size}, line_numbers={line_numbers}")

    formatter = ImageFormatter(
        style=style_inst,
        full=True,
        font_name=font_path,
        font_size=font_size,
        image_pad=pad,
        line_numbers=line_numbers,
        line_pad=line_pad,
        line_number_bg=line_number_bg,
        line_number_fg=line_number_fg,
        image_format="PNG",
    )

    try:
        image_bytes = pygments.highlight(code_string, lexer, formatter, outfile=None)
        img = Image.open(io.BytesIO(image_bytes))

        save_options = {"format": image_format}

        if image_format in ("WEBP", "JPEG"):
            save_options["quality"] = options.get("quality", 95)

        if image_format == "PNG":
            save_options["optimize"] = options.get("optimize", True)

        img.save(output_file, **save_options)

        logger.info(f"💾 Изображение сохранено: {output_file}")
        logger.info(f"✅ Генерация завершена: {scale}x, {img.size[0]}x{img.size[1]}px")

    except Exception as e:
        logger.error(f"❌ Ошибка при генерации: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    SAMPLE_CODE_TS = """
import React, { useState } from 'react';

interface UserProfile {
  username: string;
  age: number;
}
"""

    ts_options = {
        "style": "dracula",
        "font_name": "JetBrainsMono",
        "font_size": 18,
        "pad": 10,
        "format": "WEBP",
        "scale_factor": 5,
        "line_numbers": True,
        "line_pad": 5,
        "line_number_fg": "#6272A4",
    }

    create_code_screenshot(
        code_string=SAMPLE_CODE_TS.strip(),
        language="typescript",
        output_file="/tmp/typescript_screenshot_styled.webp",
        **ts_options,
    )

    SAMPLE_CODE_SQL = """
SELECT
    u.id AS user_id,
    u.username
FROM
    users u
WHERE
    u.registration_date > '2023-01-01';
"""

    sql_options = {
        "style": "github-dark",
        "font_name": "Consolas",
        "font_size": 20,
        "pad": 40,
        "format": "WEBP",
        "scale_factor": 2,
        "line_numbers": False,
    }

    create_code_screenshot(
        code_string=SAMPLE_CODE_SQL.strip(),
        language="sql",
        output_file="/tmp/sql_screenshot_no_lines.webp",
        **sql_options,
    )
