"""Тесты для guide_manager.py."""

import pytest
from pathlib import Path

from src.guide_manager import (
    get_guide,
    list_guides,
    list_themes,
    _extract_brief,
    _extract_detailed,
    GUIDES_DIR,
    THEMES_DIR,
)


class TestListGuides:
    """Тесты для list_guides()."""

    def test_list_guides_returns_list(self):
        """list_guides должен возвращать список."""
        result = list_guides()
        assert isinstance(result, list)

    def test_list_guides_has_expected_types(self):
        """list_guides должен содержать все типы гайдов."""
        result = list_guides()
        types = [g["type"] for g in result]

        assert "class" in types
        assert "sequence" in types
        assert "component" in types
        assert "activity" in types
        assert "themes" in types

    def test_list_guides_has_required_fields(self):
        """Каждый гайд должен иметь type, title и description."""
        result = list_guides()

        for guide in result:
            assert "type" in guide
            assert "title" in guide
            assert "description" in guide


class TestListThemes:
    """Тесты для list_themes()."""

    def test_list_themes_returns_list(self):
        """list_themes должен возвращать список."""
        result = list_themes()
        assert isinstance(result, list)

    def test_list_themes_has_expected_themes(self):
        """list_themes должен содержать все темы."""
        result = list_themes()
        names = [t["name"] for t in result]

        assert "default" in names
        assert "dark_gold" in names
        assert "light_fresh" in names

    def test_list_themes_has_required_fields(self):
        """Каждая тема должна иметь name и description."""
        result = list_themes()

        for theme in result:
            assert "name" in theme
            assert "description" in theme
            assert theme["description"]  # Не пустой


class TestGetGuide:
    """Тесты для get_guide()."""

    def test_get_guide_class_brief(self):
        """get_guide должен возвращать краткий гайд по class."""
        result = get_guide("class", full=False)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "<<Adapter>>" in result or "Stereotype" in result

    def test_get_guide_component_brief(self):
        """get_guide должен возвращать краткий гайд по component."""
        result = get_guide("component", full=False)

        assert isinstance(result, str)
        assert "<<Adapter>>" in result
        assert "<<Core>>" in result
        assert "<<Infrastructure>>" in result

    def test_get_guide_sequence_brief(self):
        """get_guide должен возвращать краткий гайд по sequence."""
        result = get_guide("sequence", full=False)

        assert isinstance(result, str)
        assert "participant" in result.lower() or "actor" in result.lower()

    def test_get_guide_activity_brief(self):
        """get_guide должен возвращать краткий гайд по activity."""
        result = get_guide("activity", full=False)

        assert isinstance(result, str)
        assert "start" in result.lower() or "if" in result.lower()

    def test_get_guide_themes_brief(self):
        """get_guide должен возвращать краткий гайд по themes."""
        result = get_guide("themes", full=False)

        assert isinstance(result, str)
        assert "dark_gold" in result or "light_fresh" in result

    def test_get_guide_full_longer_than_brief(self):
        """Полный гайд должен быть длиннее краткого."""
        brief = get_guide("component", full=False)
        full = get_guide("component", full=True)

        assert len(full) > len(brief)

    def test_get_guide_unknown_type(self):
        """Несуществующий тип должен вернуть сообщение об ошибке."""
        result = get_guide("unknown_type", full=False)

        assert "не найден" in result or "not found" in result.lower()
        assert "class" in result  # Показывает доступные типы


class TestExtractBrief:
    """Тесты для парсинга brief-секций.

    Примечание: Тестируем внутреннюю функцию _extract_brief напрямую
    для проверки граничных случаев парсинга маркеров.
    """

    def test_extract_brief_with_markers(self):
        """_extract_brief должен извлекать текст между маркерами."""
        content = """
Some header
<!-- BRIEF_START -->
Brief content here
<!-- BRIEF_END -->
Some footer
"""
        result = _extract_brief(content)
        assert result == "Brief content here"

    def test_extract_brief_without_markers(self):
        """_extract_brief должен вернуть начало файла без маркеров."""
        content = "A" * 600
        result = _extract_brief(content)

        assert len(result) == 503  # 500 + "..."
        assert result.endswith("...")


class TestExtractDetailed:
    """Тесты для парсинга detailed-секций.

    Примечание: Тестируем внутреннюю функцию _extract_detailed напрямую
    для проверки граничных случаев парсинга маркеров.
    """

    def test_extract_detailed_with_markers(self):
        """_extract_detailed должен извлекать текст между маркерами."""
        content = """
<!-- DETAILED_START -->
Detailed content here
<!-- DETAILED_END -->
"""
        result = _extract_detailed(content)
        assert result == "Detailed content here"

    def test_extract_detailed_without_markers(self):
        """_extract_detailed должен вернуть весь файл без маркеров."""
        content = "Full content without markers"
        result = _extract_detailed(content)

        assert result == content


class TestGuideFilesExist:
    """Тесты наличия файлов гайдов."""

    def test_guides_directory_exists(self):
        """Директория гайдов должна существовать."""
        assert GUIDES_DIR.exists()

    def test_themes_directory_exists(self):
        """Директория тем должна существовать."""
        assert THEMES_DIR.exists()

    def test_index_file_exists(self):
        """Индексный файл должен существовать."""
        index_file = GUIDES_DIR / "index.json"
        assert index_file.exists()

    def test_all_guide_files_exist(self):
        """Все файлы гайдов из index.json должны существовать."""
        guides = list_guides()

        for guide in guides:
            guide_type = guide["type"]
            if guide_type == "themes":
                file_path = GUIDES_DIR / "themes.md"
            else:
                file_path = GUIDES_DIR / f"{guide_type}_diagram.md"
            assert file_path.exists(), f"Файл {file_path} не найден"

    def test_all_theme_files_exist(self):
        """Все файлы тем должны существовать."""
        themes = list_themes()

        for theme in themes:
            theme_file = THEMES_DIR / f"{theme['name']}.puml"
            assert theme_file.exists(), f"Файл {theme_file} не найден"


class TestGuideContent:
    """Тесты содержимого гайдов."""

    def test_component_guide_has_stereotypes(self):
        """Гайд по component должен описывать стереотипы."""
        result = get_guide("component", full=True)

        assert "<<Adapter>>" in result
        assert "<<Core>>" in result
        assert "<<Infrastructure>>" in result

    def test_class_guide_has_syntax(self):
        """Гайд по class должен описывать синтаксис."""
        result = get_guide("class", full=True)

        assert "class" in result.lower()
        assert "+" in result or "public" in result.lower()

    def test_themes_guide_has_theme_names(self):
        """Гайд по themes должен содержать имена тем."""
        result = get_guide("themes", full=True)

        assert "dark_gold" in result
        assert "light_fresh" in result
        assert "default" in result
