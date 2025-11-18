#!/usr/bin/env python3

"""
Этот скрипт генерирует высококачественные изображения из исходного кода,
используя Pygments и Pillow.

Версия 4.0:
- Добавлена полная настройка нумерации строк (фон, цвет, отступы).
- Фон нумерации по умолчанию сливается с фоном стиля (как в IDE).

Перед запуском убедитесь, что вы установили необходимые зависимости:
pip install Pygments Pillow
"""

import sys
import io
from PIL import Image

# pip install pygments pillow
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters import ImageFormatter
from pygments.styles import get_style_by_name

# --- 1. Функция-оркестратор ---


def create_code_screenshot(code_string, language, output_file, **options):
    """
    Создает скриншот фрагмента кода и сохраняет его в файл.
    :param code_string: Строка с исходным кодом.
    :param language: Язык программирования (для лексера Pygments).
    :param output_file: Путь к выходному файлу изображения.
    :param options: Дополнительные параметры настройки (см. ниже).
    Поддерживаемые параметры в options:
        - style: Название стиля Pygments (по умолчанию 'monokai').
        - font_name: Имя шрифта (по умолчанию 'Consolas').
        - font_size: Размер шрифта (по умолчанию 18).
        - pad: Отступ вокруг кода (по умолчанию 25).
        - format: Формат изображения ('PNG', 'JPEG', 'WEBP'; по умолчанию 'WEBP').
        - scale_factor: Фактор масштабирования (по умолчанию 3).
        - transparent: Логическое значение для прозрачного фона (по умолчанию False).
        - line_numbers: Включить нумерацию строк (по умолчанию True).
        - line_pad: Отступ между номерами строк и кодом (по умолчанию 10).
        - line_number_bg: Цвет фона номеров строк (по умолчанию цвет фона стиля).
        - line_number_fg: Цвет текста номеров строк (по умолчанию '#888888').
        - quality: Качество для JPEG/WEBP (по умолчанию 95).
        - optimize: Оптимизация для PNG (по умолчанию True).
    """

    print(f"Генерация скриншота для языка: {language}...")

    # --- 2. Получение "Лексера" (анализатора языка) ---
    try:
        lexer = get_lexer_by_name(language, stripall=True)
    except pygments.util.ClassNotFound:
        print(f"Ошибка: Лексер для языка '{language}' не найден. Используется 'text'.")
        lexer = get_lexer_by_name("text", stripall=True)

    # --- 3. Сбор и настройка опций ---

    # --- A: Основной стиль и фон ---
    style_name = options.get("style", "monokai")
    style_inst = get_style_by_name(style_name)

    transparent = options.get("transparent", False)
    image_format = options.get("format", "WEBP").upper()

    if transparent:
        style_inst.background_color = None
        if image_format not in ("PNG", "WEBP"):
            print("Предупреждение: Прозрачность поддерживается только в PNG и WEBP.")
            image_format = "PNG"

    # --- B: Масштабирование (как мы и договорились) ---
    scale = options.get("scale_factor", 3)

    font_name = options.get("font_name", "Consolas")
    font_size = options.get("font_size", 18) * scale

    # --- C: НОВЫЕ НАСТРОЙКИ НУМЕРАЦИИ ---
    line_numbers = options.get("line_numbers", True)

    # Отступ (базовый) * scale. Теперь ты можешь передать 'line_pad': 5
    line_pad = options.get("line_pad", 10) * scale

    # Цвет фона номеров: по умолчанию = цвету фона стиля.
    # Это создает эффект "как в редакторе".
    line_number_bg = options.get("line_number_bg", style_inst.background_color)

    # Цвет цифр: по умолчанию - приглушенный серый.
    line_number_fg = options.get("line_number_fg", "#888888")

    # --- D: Общие отступы ---
    pad = options.get("pad", 25) * scale

    # --- 4. Создание "Форматтера" (самого рисовальщика) ---
    # Передаем в него ВСЕ наши новые опции

    formatter = ImageFormatter(
        style=style_inst,
        full=True,
        font_name=font_name,
        font_size=font_size,
        image_pad=pad,
        # --- Параметры нумерации ---
        line_numbers=line_numbers,
        line_pad=line_pad,  # <-- Наш настраиваемый отступ
        line_number_bg=line_number_bg,  # <-- Наш настраиваемый фон
        line_number_fg=line_number_fg,  # <-- Наш настраиваемый цвет цифр
        image_format="PNG",
    )

    # --- 5. Генерация в память и ручное сохранение через Pillow ---

    try:
        # Шаг 1: Генерируем PNG в байты
        image_bytes = pygments.highlight(code_string, lexer, formatter, outfile=None)

        # Шаг 2: Открываем эти байты с помощью Pillow
        img = Image.open(io.BytesIO(image_bytes))

        # Шаг 3: Готовим опции сохранения
        save_options = {
            "format": image_format,
        }

        if image_format in ("WEBP", "JPEG"):
            save_options["quality"] = options.get("quality", 95)

        if image_format == "PNG":
            save_options["optimize"] = options.get("optimize", True)

        # Шаг 4: Сохраняем
        img.save(output_file, **save_options)

        print(f"Успешно сохранено в: {output_file} (Формат: {image_format})")
        print(f"-> Масштаб: {scale}x, Итоговый размер: {img.size[0]}x{img.size[1]}px")

    except Exception as e:
        print(f"Ошибка при генерации или сохранении файла: {e}")
        print(f"Возможная причина: шрифт '{font_name}' не найден в системе.")


# --- Демонстрационный блок для запуска скрипта ---

if __name__ == "__main__":
    # --- Пример 1: TypeScript (3x масштаб) с настроенными номерами ---

    SAMPLE_CODE_TS = """
import React, { useState } from 'react';

// Определение простого интерфейса
interface UserProfile {
  username: string;
  age: number;
}
    """

    ts_options = {
        "style": "dracula",
        "font_name": "Consolas",
        "font_size": 18,
        "pad": 10,
        "format": "WEBP",
        "scale_factor": 5,
        # --- Вот как ты теперь этим управляешь ---
        "line_numbers": True,
        "line_pad": 5,  # <-- Уменьшили отступ (базовый)
        "line_number_fg": "#6272A4",  # <-- Цвет комментариев из темы Dracula
        # 'line_number_bg' не указываем, он АВТОМАТИЧЕСКИ
        # возьмется из стиля 'dracula' (будет темно-серым)
    }

    create_code_screenshot(
        code_string=SAMPLE_CODE_TS.strip(),
        language="typescript",
        output_file="typescript_screenshot_styled.webp",
        **ts_options,
    )

    print("-" * 20)

    # --- Пример 2: SQL (2x масштаб) без номеров ---

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
        "line_numbers": False,  # <-- Просто отключаем их
    }

    create_code_screenshot(
        code_string=SAMPLE_CODE_SQL.strip(),
        language="sql",
        output_file="sql_screenshot_no_lines.webp",
        **sql_options,
    )
