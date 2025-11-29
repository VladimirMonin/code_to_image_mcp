"""Диагностика работы шрифтов в PlantUML."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from diagram_renderer import render_diagram_from_string


class TestFontDiagnostic:
    """Визуальные тесты для проверки различий шрифтов."""

    @pytest.fixture
    def comparison_diagram(self):
        """Диаграмма для визуального сравнения разных шрифтов."""
        return """
@startuml
skinparam defaultFontSize 16
skinparam backgroundColor #FFFFFF

rectangle "Default Font" {
  note
    ABCDEFGHIJKLMNOPQRSTUVWXYZ
    abcdefghijklmnopqrstuvwxyz
    0123456789 !@#$%^&*()
    Illegal != 0
  end note
}
@enduml
"""

    def test_font_arial(self, output_dir, comparison_diagram):
        """Тест с Arial (для сравнения)."""
        code = comparison_diagram.replace("Default Font", "Arial Font")
        code = code.replace("@startuml", '@startuml\nskinparam defaultFontName "Arial"')

        output_file = output_dir / "font_arial.png"

        result = render_diagram_from_string(
            diagram_code=code,
            output_path=str(output_file),
            format="png",
            theme_name=None,  # БЕЗ темы
        )

        assert result["success"] is True
        print(f"\n📄 Arial: {output_file}")

    def test_font_jetbrains_mono(self, output_dir, comparison_diagram):
        """Тест с JetBrains Mono."""
        code = comparison_diagram.replace("Default Font", "JetBrains Mono Font")
        code = code.replace(
            "@startuml", '@startuml\nskinparam defaultFontName "JetBrains Mono"'
        )

        output_file = output_dir / "font_jetbrains_mono.png"

        result = render_diagram_from_string(
            diagram_code=code,
            output_path=str(output_file),
            format="png",
            theme_name=None,
        )

        assert result["success"] is True
        print(f"\n📄 JetBrains Mono: {output_file}")

    def test_font_fira_code(self, output_dir, comparison_diagram):
        """Тест с Fira Code."""
        code = comparison_diagram.replace("Default Font", "Fira Code Font")
        code = code.replace(
            "@startuml", '@startuml\nskinparam defaultFontName "Fira Code"'
        )

        output_file = output_dir / "font_fira_code.png"

        result = render_diagram_from_string(
            diagram_code=code,
            output_path=str(output_file),
            format="png",
            theme_name=None,
        )

        assert result["success"] is True
        print(f"\n📄 Fira Code: {output_file}")

    def test_font_courier_new(self, output_dir, comparison_diagram):
        """Тест с Courier New (системный шрифт)."""
        code = comparison_diagram.replace("Default Font", "Courier New Font")
        code = code.replace(
            "@startuml", '@startuml\nskinparam defaultFontName "Courier New"'
        )

        output_file = output_dir / "font_courier_new.png"

        result = render_diagram_from_string(
            diagram_code=code,
            output_path=str(output_file),
            format="png",
            theme_name=None,
        )

        assert result["success"] is True
        print(f"\n📄 Courier New: {output_file}")

    def test_check_gdi_loaded_fonts(self):
        """Проверка, что load_custom_fonts действительно вызывается."""
        import logging
        from font_manager import load_custom_fonts

        # Включаем подробное логирование
        logging.basicConfig(level=logging.DEBUG)

        # Вызываем напрямую
        load_custom_fonts()

        # Если нет исключений - хорошо
        assert True
