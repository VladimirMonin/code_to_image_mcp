"""Менеджер шрифтов для работы с локальными TTF файлами и системной регистрации.

Функции:
    get_font_path(font_name) -> str
        Возвращает путь к шрифту.
    list_available_fonts() -> list[str]
        Возвращает список доступных шрифтов.
    load_custom_fonts() -> None
        Временно регистрирует шрифты в системе (Windows) для видимости в Java.
"""

import logging
import platform
import ctypes
from pathlib import Path

logger = logging.getLogger(__name__)

FONTS_DIR = Path(__file__).parent.parent / "asset" / "fonts"

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


def load_custom_fonts() -> None:
    """
    Временно регистрирует шрифты из asset/fonts в GDI сессии Windows.
    Это необходимо, чтобы внешние процессы (например, Java/PlantUML) видели
    эти шрифты без их физической установки в папку C:/Windows/Fonts.
    """
    if platform.system() != "Windows":
        logger.debug("🐧 Пропуск регистрации шрифтов (не Windows)")
        return

    # Флаг FR_PRIVATE (0x10) делает шрифт видимым для процесса и его дочерних элементов,
    # и удаляет его при завершении процесса. Это идеально для портабельности.
    FR_PRIVATE = 0x10

    loaded_count = 0

    # Сканируем реальные файлы в директории
    if not FONTS_DIR.exists():
        logger.warning(f"⚠️ Папка шрифтов не найдена: {FONTS_DIR}")
        return

    for font_file in FONTS_DIR.glob("*.ttf"):
        try:
            # Преобразуем путь в строку
            path_str = str(font_file.absolute())

            # Вызов Windows API AddFontResourceExW
            # gdi32.dll должен быть доступен на любой Windows
            res = ctypes.windll.gdi32.AddFontResourceExW(path_str, FR_PRIVATE, 0)

            if res > 0:
                loaded_count += 1
                logger.debug(f"💉 Шрифт временно зарегистрирован: {font_file.name}")
            else:
                # Если вернул 0, возможно шрифт уже загружен или ошибка пути
                logger.debug(
                    f"⚠️ Шрифт не был зарегистрирован (возможно уже есть): {font_file.name}"
                )

        except Exception as e:
            logger.error(f"❌ Ошибка GDI при загрузке шрифта {font_file.name}: {e}")

    if loaded_count > 0:
        logger.info(f"💉 Временно активировано шрифтов для сессии: {loaded_count}")
