"""Менеджер гайдов по PlantUML.

Модуль обеспечивает чтение и парсинг markdown-гайдов для помощи
AI-агентам в правильном использовании PlantUML синтаксиса.

Функции:
    get_guide(guide_type, full=False) -> str
        Возвращает содержимое гайда (brief или full версию).
    list_guides() -> list[dict]
        Возвращает список доступных гайдов с метаданными.
    list_themes() -> list[dict]
        Возвращает список доступных тем оформления.
"""

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Константы путей
GUIDES_DIR = Path(__file__).parent.parent / "doc" / "plantuml_guides"
THEMES_DIR = Path(__file__).parent.parent / "asset" / "themes"
INDEX_FILE = GUIDES_DIR / "index.json"

# Маркеры для парсинга brief/detailed секций
BRIEF_START = "<!-- BRIEF_START -->"
BRIEF_END = "<!-- BRIEF_END -->"
DETAILED_START = "<!-- DETAILED_START -->"
DETAILED_END = "<!-- DETAILED_END -->"


def _load_index() -> dict:
    """Загружает индекс гайдов из index.json."""
    if not INDEX_FILE.exists():
        logger.warning(f"⚠️ Индексный файл не найден: {INDEX_FILE}")
        return {"guides": []}

    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"❌ Ошибка парсинга index.json: {e}")
        return {"guides": []}


def _extract_brief(content: str) -> str:
    """Извлекает brief-секцию из markdown-контента.

    Args:
        content: Полное содержимое markdown-файла.

    Returns:
        Текст между маркерами BRIEF_START и BRIEF_END,
        или первые 500 символов если маркеры не найдены.
    """
    match = re.search(
        rf"{re.escape(BRIEF_START)}(.*?){re.escape(BRIEF_END)}",
        content,
        re.DOTALL,
    )

    if match:
        return match.group(1).strip()

    logger.debug("🔍 Маркеры BRIEF не найдены, возвращаем начало файла")
    return content[:500] + "..." if len(content) > 500 else content


def _extract_detailed(content: str) -> str:
    """Извлекает detailed-секцию из markdown-контента.

    Args:
        content: Полное содержимое markdown-файла.

    Returns:
        Текст между маркерами DETAILED_START и DETAILED_END,
        или весь файл если маркеры не найдены.
    """
    match = re.search(
        rf"{re.escape(DETAILED_START)}(.*?){re.escape(DETAILED_END)}",
        content,
        re.DOTALL,
    )

    if match:
        return match.group(1).strip()

    logger.debug("🔍 Маркеры DETAILED не найдены, возвращаем весь файл")
    return content


def get_guide(guide_type: str, full: bool = False) -> str:
    """Возвращает содержимое гайда по типу диаграммы.

    Args:
        guide_type: Тип гайда (class, sequence, component, activity, themes).
        full: Если True — возвращает полную версию, иначе — краткую.

    Returns:
        Содержимое гайда или сообщение об ошибке с доступными гайдами.
    """
    logger.info(f"📚 Запрос гайда: type={guide_type}, full={full}")

    index = _load_index()
    guides = index.get("guides", [])

    guide_info = None
    for g in guides:
        if g.get("type") == guide_type:
            guide_info = g
            break

    if not guide_info:
        available = [g.get("type") for g in guides]
        logger.warning(f"⚠️ Гайд не найден: {guide_type}")
        return (
            f"Гайд '{guide_type}' не найден.\n\n"
            f"Доступные гайды: {', '.join(available)}\n\n"
            f"Используйте list_guides() для получения полного списка."
        )

    guide_file = GUIDES_DIR / guide_info.get("file", f"{guide_type}_diagram.md")

    if not guide_file.exists():
        logger.error(f"❌ Файл гайда не найден: {guide_file}")
        return f"Файл гайда не найден: {guide_file}"

    try:
        with open(guide_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error(f"❌ Ошибка чтения гайда: {e}")
        return f"Ошибка чтения гайда: {e}"

    if full:
        brief = _extract_brief(content)
        detailed = _extract_detailed(content)
        logger.debug(
            f"📖 Возвращаем полный гайд: {len(brief) + len(detailed)} символов"
        )
        return f"{brief}\n\n{detailed}"
    else:
        brief = _extract_brief(content)
        logger.debug(f"📖 Возвращаем краткий гайд: {len(brief)} символов")
        return brief


def list_guides() -> list[dict]:
    """Возвращает список доступных гайдов с метаданными.

    Returns:
        Список словарей с информацией о гайдах:
        [{"type": "class", "title": "...", "description": "..."}]
    """
    logger.info("📚 Запрос списка гайдов")

    index = _load_index()
    guides = index.get("guides", [])

    result = []
    for g in guides:
        result.append(
            {
                "type": g.get("type"),
                "title": g.get("title"),
                "description": g.get("description"),
            }
        )

    logger.debug(f"📋 Найдено гайдов: {len(result)}")
    return result


def list_themes() -> list[dict]:
    """Возвращает список доступных тем оформления.

    Сканирует директорию asset/themes/ и возвращает информацию
    о каждой теме на основе комментариев в файле.

    Returns:
        Список словарей с информацией о темах:
        [{"name": "dark_gold", "description": "..."}]
    """
    logger.info("🎨 Запрос списка тем")

    if not THEMES_DIR.exists():
        logger.warning(f"⚠️ Директория тем не найдена: {THEMES_DIR}")
        return []

    themes = []
    theme_descriptions = {
        "default": "Современная тёмная тема в стиле VS Code. Универсальная.",
        "dark_gold": "Строгая тёмная тема с золотым акцентом для презентаций.",
        "light_fresh": "Мягкая светлая тема с мятными тонами для документации.",
    }

    for theme_file in sorted(THEMES_DIR.glob("*.puml")):
        name = theme_file.stem

        description = theme_descriptions.get(name)
        if not description:
            try:
                with open(theme_file, "r", encoding="utf-8") as f:
                    first_lines = f.read(500)
                    match = re.search(r"'\s*===\s*THEME:\s*(.+?)\s*===", first_lines)
                    if match:
                        description = match.group(1).strip()
                    else:
                        match = re.search(r"'\s*(.+)", first_lines)
                        if match:
                            description = match.group(1).strip()
                        else:
                            description = f"Тема {name}"
            except Exception:
                description = f"Тема {name}"

        themes.append({"name": name, "description": description})

    logger.debug(f"🎨 Найдено тем: {len(themes)}")
    return themes


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("=== Guide Manager Test ===\n")

    print("1. Список гайдов:")
    for guide in list_guides():
        print(f"   - {guide['type']}: {guide['title']}")

    print("\n2. Список тем:")
    for theme in list_themes():
        print(f"   - {theme['name']}: {theme['description']}")

    print("\n3. Краткий гайд по component:")
    print(get_guide("component", full=False)[:300] + "...")

    print("\n4. Несуществующий гайд:")
    print(get_guide("unknown"))
