"""Тесты для diagram_renderer модуля."""

import pytest
from pathlib import Path
import sys

# Добавляем корень проекта в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from diagram_renderer import (
    render_diagram_from_string,
    ensure_java_environment,
    JavaNotFoundError,
    PlantUMLRenderError,
)


class TestJavaEnvironment:
    """Тесты проверки Java окружения."""

    def test_java_is_available(self):
        """Проверка наличия Java в системе."""
        version = ensure_java_environment()
        assert version is not None
        assert len(version) > 0
        # Проверяем что это действительно версия Java
        assert "java" in version.lower() or "openjdk" in version.lower()

    def test_java_version_format(self):
        """Проверка формата версии Java."""
        version = ensure_java_environment()
        # Версия должна содержать цифры
        assert any(char.isdigit() for char in version)


class TestBasicRendering:
    """Базовые тесты рендеринга диаграмм."""

    def test_render_simple_sequence_diagram_png(self, output_dir, test_plantuml_code):
        """Рендеринг простой sequence диаграммы в PNG."""
        output_file = output_dir / "test_simple_sequence.png"

        result = render_diagram_from_string(
            diagram_code=test_plantuml_code,
            output_path=str(output_file),
            format="png",
            theme_name="default",
        )

        assert result["success"] is True
        assert output_file.exists()
        assert result["format"] == "png"
        assert result["file_size_kb"] > 0
        assert "java_version" in result
        assert result["theme_used"] == "default"

    def test_render_simple_sequence_diagram_svg(self, output_dir, test_plantuml_code):
        """Рендеринг простой sequence диаграммы в SVG."""
        output_file = output_dir / "test_simple_sequence.svg"

        result = render_diagram_from_string(
            diagram_code=test_plantuml_code,
            output_path=str(output_file),
            format="svg",
            theme_name="default",
        )

        assert result["success"] is True
        assert output_file.exists()
        assert result["format"] == "svg"
        assert result["file_size_kb"] > 0

    def test_render_without_theme(self, output_dir, test_plantuml_code):
        """Рендеринг без темы оформления."""
        output_file = output_dir / "test_no_theme.png"

        result = render_diagram_from_string(
            diagram_code=test_plantuml_code,
            output_path=str(output_file),
            format="png",
            theme_name=None,
        )

        assert result["success"] is True
        assert output_file.exists()
        assert result["theme_used"] is None


class TestCyrillicSupport:
    """Тесты поддержки кириллицы."""

    def test_render_cyrillic_sequence_diagram(
        self, output_dir, test_plantuml_code_cyrillic
    ):
        """Рендеринг диаграммы с кириллицей."""
        output_file = output_dir / "test_cyrillic_sequence.png"

        result = render_diagram_from_string(
            diagram_code=test_plantuml_code_cyrillic,
            output_path=str(output_file),
            format="png",
            theme_name="default",
        )

        assert result["success"] is True
        assert output_file.exists()
        assert result["file_size_kb"] > 0

    def test_render_cyrillic_class_diagram(self, output_dir):
        """Рендеринг классовой диаграммы с кириллицей."""
        code = """
@startuml
!pragma layout smetana

class Пользователь {
  -имя: str
  -email: str
  +войти()
  +выйти()
}

class Заказ {
  -номер: int
  -сумма: float
  +создать()
  +отменить()
}

Пользователь "1" -- "*" Заказ : создаёт >
@enduml
"""
        output_file = output_dir / "test_cyrillic_class.svg"

        result = render_diagram_from_string(
            diagram_code=code,
            output_path=str(output_file),
            format="svg",
            theme_name="default",
        )

        assert result["success"] is True
        assert output_file.exists()


class TestDifferentDiagramTypes:
    """Тесты разных типов диаграмм."""

    def test_activity_diagram(self, output_dir):
        """Рендеринг activity диаграммы."""
        code = """
@startuml
start
:Начало процесса;
if (Условие выполнено?) then (да)
  :Выполнить действие А;
else (нет)
  :Выполнить действие Б;
endif
:Завершение;
stop
@enduml
"""
        output_file = output_dir / "test_activity.png"

        result = render_diagram_from_string(
            diagram_code=code,
            output_path=str(output_file),
            format="png",
            theme_name="default",
        )

        assert result["success"] is True
        assert output_file.exists()

    def test_use_case_diagram(self, output_dir):
        """Рендеринг use case диаграммы."""
        code = """
@startuml
!pragma layout smetana
left to right direction
actor Пользователь
actor Администратор

rectangle Система {
  Пользователь -- (Войти в систему)
  Пользователь -- (Просмотр данных)
  Администратор -- (Управление пользователями)
  Администратор -- (Просмотр данных)
}
@enduml
"""
        output_file = output_dir / "test_usecase.png"

        result = render_diagram_from_string(
            diagram_code=code,
            output_path=str(output_file),
            format="png",
            theme_name="default",
        )

        assert result["success"] is True
        assert output_file.exists()

    def test_component_diagram(self, output_dir):
        """Рендеринг component диаграммы."""
        code = """
@startuml
!pragma layout smetana
package "Web Application" {
  [Frontend] as FE
  [Backend API] as BE
  [Database] as DB
}

FE --> BE : HTTP/REST
BE --> DB : SQL
@enduml
"""
        output_file = output_dir / "test_component.png"

        result = render_diagram_from_string(
            diagram_code=code,
            output_path=str(output_file),
            format="png",
            theme_name="default",
        )

        assert result["success"] is True
        assert output_file.exists()


class TestErrorHandling:
    """Тесты обработки ошибок."""

    def test_invalid_theme_name(self, output_dir, test_plantuml_code):
        """Попытка использовать несуществующую тему."""
        output_file = output_dir / "test_invalid_theme.png"

        with pytest.raises(FileNotFoundError) as exc_info:
            render_diagram_from_string(
                diagram_code=test_plantuml_code,
                output_path=str(output_file),
                format="png",
                theme_name="nonexistent_theme",
            )

        assert "Тема не найдена" in str(exc_info.value)

    def test_create_output_directory(self, output_dir, test_plantuml_code):
        """Автоматическое создание директории для вывода."""
        output_file = output_dir / "subdir" / "nested" / "test.png"

        result = render_diagram_from_string(
            diagram_code=test_plantuml_code,
            output_path=str(output_file),
            format="png",
            theme_name="default",
        )

        assert result["success"] is True
        assert output_file.exists()


class TestFormats:
    """Тесты различных форматов вывода."""

    @pytest.mark.parametrize("format", ["png", "svg"])
    def test_different_formats(self, output_dir, test_plantuml_code, format):
        """Тест различных форматов вывода."""
        output_file = output_dir / f"test_format.{format}"

        result = render_diagram_from_string(
            diagram_code=test_plantuml_code,
            output_path=str(output_file),
            format=format,
            theme_name="default",
        )

        assert result["success"] is True
        assert output_file.exists()
        assert result["format"] == format
        assert output_file.suffix == f".{format}"
