"""Тесты модуля font_initializer."""

import pytest
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from font_initializer import ensure_fonts_initialized, MARKER_FILE


class TestFontInitializer:
    """Тесты инициализатора шрифтов."""

    def test_ensure_fonts_initialized_success(self):
        """Проверка успешной инициализации шрифтов."""
        result = ensure_fonts_initialized()

        assert result["success"] is True
        assert result["java_home"] is not None
        assert len(result["fonts"]) > 0
        assert result["error"] is None

        # Проверяем наличие ключевых шрифтов
        fonts = result["fonts"]
        assert any("JetBrains" in font for font in fonts)
        assert any("Fira" in font for font in fonts)

    def test_marker_file_created(self):
        """Проверка создания маркер-файла."""
        # Вызываем инициализацию
        ensure_fonts_initialized()

        # Проверяем наличие маркера
        assert MARKER_FILE.exists()

        # Проверяем содержимое
        with open(MARKER_FILE, "r") as f:
            data = json.load(f)

        assert "java_home" in data
        assert "fonts_installed" in data
        assert "platform" in data
        assert "timestamp" in data

        assert len(data["fonts_installed"]) > 0

    def test_second_call_uses_cache(self):
        """Проверка что второй вызов использует кеш."""
        # Первый вызов
        result1 = ensure_fonts_initialized()
        assert result1["success"] is True

        # Второй вызов (должен использовать кеш)
        result2 = ensure_fonts_initialized()
        assert result2["success"] is True
        assert result2["already_installed"] is True

        # Оба результата должны быть идентичны
        assert result1["java_home"] == result2["java_home"]
        assert set(result1["fonts"]) == set(result2["fonts"])

    def test_fonts_in_jre(self):
        """Проверка что шрифты действительно скопированы в JRE."""
        result = ensure_fonts_initialized()
        assert result["success"] is True

        # Проверяем физическое наличие файлов
        java_home = Path(result["java_home"])

        # Возможные пути к fonts директории
        possible_paths = [
            java_home / "lib" / "fonts",
            java_home / "jre" / "lib" / "fonts",
        ]

        fonts_dir = None
        for path in possible_paths:
            if path.exists():
                fonts_dir = path
                break

        assert fonts_dir is not None, "Директория шрифтов JRE не найдена"

        # Проверяем наличие наших шрифтов
        ttf_files = list(fonts_dir.glob("*.ttf"))
        font_names = [f.name for f in ttf_files]

        assert any("JetBrains" in name for name in font_names)
        assert any("Fira" in name for name in font_names)
