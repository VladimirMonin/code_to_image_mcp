"""Тесты интеграции шрифтов с PlantUML."""

import pytest
from pathlib import Path
import sys
import platform

# Добавляем корень проекта в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.diagram_renderer import render_diagram_from_string
from src.font_manager import load_custom_fonts, FONTS_DIR


class TestFontLoading:
    """Тесты загрузки и регистрации шрифтов."""

    def test_fonts_directory_exists(self):
        """Проверка существования директории со шрифтами."""
        assert FONTS_DIR.exists(), f"Директория шрифтов не найдена: {FONTS_DIR}"

    def test_jetbrains_mono_font_exists(self):
        """Проверка наличия файла JetBrains Mono."""
        jetbrains_font = FONTS_DIR / "JetBrainsMono-Regular.ttf"
        assert jetbrains_font.exists(), (
            f"Шрифт JetBrains Mono не найден: {jetbrains_font}"
        )

    def test_firacode_font_exists(self):
        """Проверка наличия файла Fira Code."""
        fira_font = FONTS_DIR / "FiraCode-Regular.ttf"
        assert fira_font.exists(), f"Шрифт Fira Code не найден: {fira_font}"

    @pytest.mark.skipif(
        platform.system() != "Windows", reason="Тест только для Windows"
    )
    def test_load_custom_fonts_no_error(self):
        """Проверка, что load_custom_fonts() выполняется без ошибок."""
        # Не должно быть исключений
        load_custom_fonts()


class TestDiagramWithCustomFonts:
    """Тесты рендеринга диаграмм с кастомными шрифтами."""

    @pytest.fixture
    def diagram_code_with_jetbrains(self):
        """PlantUML код с указанием JetBrains Mono."""
        return """
@startuml
skinparam defaultFontName "JetBrains Mono"
skinparam defaultFontSize 14

class CodeToImageMCP {
  + generate_code_screenshot()
  + render_diagram_from_string()
  - load_custom_fonts()
}

class FontManager {
  + get_font_path()
  + list_available_fonts()
  + load_custom_fonts()
}

CodeToImageMCP --> FontManager : uses
@enduml
"""

    @pytest.fixture
    def diagram_code_with_firacode(self):
        """PlantUML код с указанием Fira Code."""
        return """
@startuml
skinparam defaultFontName "Fira Code"

Alice -> Bob: Hello != World
Bob -> Alice: foo() => bar()
note right: Ligatures: -> => != <=
@enduml
"""

    def test_render_with_jetbrains_mono(self, output_dir, diagram_code_with_jetbrains):
        """Рендеринг диаграммы с JetBrains Mono."""
        output_file = output_dir / "test_jetbrains_mono.png"

        result = render_diagram_from_string(
            diagram_code=diagram_code_with_jetbrains,
            output_path=str(output_file),
            format="png",
            theme_name="default",
        )

        assert result["success"] is True
        assert output_file.exists()
        assert output_file.stat().st_size > 0
        print(f"\n✅ Диаграмма с JetBrains Mono создана: {output_file}")

    def test_render_with_firacode(self, output_dir, diagram_code_with_firacode):
        """Рендеринг диаграммы с Fira Code."""
        output_file = output_dir / "test_firacode.png"

        result = render_diagram_from_string(
            diagram_code=diagram_code_with_firacode,
            output_path=str(output_file),
            format="png",
            theme_name="default",
        )

        assert result["success"] is True
        assert output_file.exists()
        assert output_file.stat().st_size > 0
        print(f"\n✅ Диаграмма с Fira Code создана: {output_file}")

    def test_render_class_diagram_with_cyrillic_jetbrains(self, output_dir):
        """Рендеринг class диаграммы с кириллицей и JetBrains Mono."""
        diagram_code = """
@startuml
skinparam defaultFontName "JetBrains Mono"
skinparam classAttributeFontSize 12
skinparam classFontSize 14

class РендерерДиаграмм {
  - java_version: str
  - plantuml_jar: Path
  + render_diagram_from_string()
  + ensure_java_environment()
}

class МенеджерШрифтов {
  - fonts_dir: Path
  + get_font_path()
  + load_custom_fonts()
}

РендерерДиаграмм --> МенеджерШрифтов : использует
@enduml
"""
        output_file = output_dir / "test_cyrillic_jetbrains.png"

        result = render_diagram_from_string(
            diagram_code=diagram_code,
            output_path=str(output_file),
            format="png",
            theme_name="default",
        )

        assert result["success"] is True
        assert output_file.exists()
        assert output_file.stat().st_size > 0
        print(f"\n✅ Диаграмма с кириллицей и JetBrains Mono: {output_file}")
