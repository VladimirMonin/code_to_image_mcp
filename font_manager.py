"""Менеджер шрифтов для работы с локальными TTF файлами."""

from pathlib import Path

# Папка с шрифтами относительно этого файла
FONTS_DIR = Path(__file__).parent / "asset" / "fonts"

# Маппинг имён на файлы
AVAILABLE_FONTS = {
    "JetBrainsMono": "JetBrainsMono-Regular.ttf",
    "FiraCode": "FiraCode-Regular.ttf",
    "CascadiaCode": "CascadiaCode-Regular.ttf",
    # Системные шрифты (fallback)
    "Consolas": None,  # будет использован системный
    "Courier New": None,
}


def get_font_path(font_name: str) -> str:
    """Получить абсолютный путь к шрифту.

    Args:
        font_name: Имя шрифта из AVAILABLE_FONTS

    Returns:
        Абсолютный путь к TTF файлу или имя системного шрифта

    Raises:
        ValueError: Если шрифт не найден
    """

    if font_name not in AVAILABLE_FONTS:
        raise ValueError(
            f"Шрифт '{font_name}' не найден. "
            f"Доступные: {', '.join(AVAILABLE_FONTS.keys())}"
        )

    ttf_file = AVAILABLE_FONTS[font_name]

    # Если это системный шрифт (None), возвращаем имя как есть
    if ttf_file is None:
        return font_name

    # Иначе строим абсолютный путь
    font_path = FONTS_DIR / ttf_file

    if not font_path.exists():
        raise FileNotFoundError(
            f"Файл шрифта не найден: {font_path}\n"
            f"Убедитесь, что файл '{ttf_file}' находится в папке asset/fonts/"
        )

    return str(font_path.absolute())


def list_available_fonts() -> list[str]:
    """Получить список всех доступных шрифтов."""
    return list(AVAILABLE_FONTS.keys())
