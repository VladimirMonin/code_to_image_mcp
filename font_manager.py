"""Менеджер шрифтов для работы с локальными TTF файлами.

Функции:
    get_font_path(font_name) -> str
        Возвращает путь к шрифту.
    list_available_fonts() -> list[str]
        Возвращает список доступных шрифтов.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

FONTS_DIR = Path(__file__).parent / "asset" / "fonts"

AVAILABLE_FONTS = {
    "JetBrainsMono": "JetBrainsMono-Regular.ttf",
    "FiraCode": "FiraCode-Regular.ttf",
    "CascadiaCode": "CascadiaCode-Regular.ttf",
    "Consolas": None,
    "Courier New": None,
}


def get_font_path(font_name: str) -> str:
    """Возвращает путь к шрифту.

    Args:
        font_name: Имя шрифта из AVAILABLE_FONTS.

    Returns:
        Абсолютный путь к TTF файлу или имя системного шрифта.

    Raises:
        ValueError: Если шрифт не найден в списке доступных.
        FileNotFoundError: Если TTF файл шрифта отсутствует.
    """
    logger.debug(f"🔍 Поиск шрифта: {font_name}")

    if font_name not in AVAILABLE_FONTS:
        logger.error(f"❌ Шрифт '{font_name}' не найден")
        raise ValueError(
            f"Шрифт '{font_name}' не найден. "
            f"Доступные: {', '.join(AVAILABLE_FONTS.keys())}"
        )

    ttf_file = AVAILABLE_FONTS[font_name]

    if ttf_file is None:
        logger.debug(f"📦 Использование системного шрифта: {font_name}")
        return font_name

    font_path = FONTS_DIR / ttf_file

    if not font_path.exists():
        logger.error(f"❌ Файл шрифта не найден: {font_path}")
        raise FileNotFoundError(
            f"Файл шрифта не найден: {font_path}\n"
            f"Убедитесь, что файл '{ttf_file}' находится в папке asset/fonts/"
        )

    logger.info(f"📦 Загружен шрифт: {font_path}")
    return str(font_path.absolute())


def list_available_fonts() -> list[str]:
    """Возвращает список доступных шрифтов."""
    return list(AVAILABLE_FONTS.keys())
