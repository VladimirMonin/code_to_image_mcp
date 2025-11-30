"""Тесты для diagram_renderer модуля."""

import pytest
from pathlib import Path
import sys

# Добавляем корень проекта в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.diagram_renderer import (
    render_diagram_from_string,
    render_diagram_to_image,
    ensure_java_environment,
    JavaNotFoundError,
    PlantUMLRenderError,
    PlantUMLSyntaxError,
)
from PIL import Image
from src.image_utils import save_image, convert_to_webp


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


class TestRenderToImage:
    """Тесты новой функции render_diagram_to_image()."""

    def test_render_to_image_returns_pil_image(self, test_plantuml_code):
        """Тест что render_diagram_to_image() возвращает PIL Image."""
        image = render_diagram_to_image(
            diagram_code=test_plantuml_code,
            format="png",
            theme_name="default",
            scale_factor=1.0,
        )

        assert isinstance(image, Image.Image)
        assert image.width > 0
        assert image.height > 0
        assert image.mode == "RGB"

    def test_render_to_image_scale_factor_1x(self, test_plantuml_code):
        """Тест рендеринга с scale_factor=1.0 (96 DPI)."""
        image = render_diagram_to_image(
            diagram_code=test_plantuml_code,
            format="png",
            theme_name="default",
            scale_factor=1.0,
        )

        # Сохраняем ширину для сравнения
        width_1x = image.width
        height_1x = image.height

        assert width_1x > 0
        assert height_1x > 0

    def test_render_to_image_scale_factor_3x(self, test_plantuml_code):
        """Тест рендеринга с scale_factor=3.0 (288 DPI) - для 4K/print."""
        image_1x = render_diagram_to_image(
            diagram_code=test_plantuml_code,
            format="png",
            theme_name="default",
            scale_factor=1.0,
        )

        image_3x = render_diagram_to_image(
            diagram_code=test_plantuml_code,
            format="png",
            theme_name="default",
            scale_factor=3.0,
        )

        # 3x должен быть примерно в 3 раза больше
        assert image_3x.width > image_1x.width * 2.5
        assert image_3x.height > image_1x.height * 2.5

    def test_render_to_image_with_webp_conversion(self, test_plantuml_code, output_dir):
        """Тест конверсии PIL Image в WebP через image_utils."""
        image = render_diagram_to_image(
            diagram_code=test_plantuml_code,
            format="png",
            theme_name="default",
            scale_factor=2.0,
        )

        # Конвертируем в WebP
        webp_bytes = convert_to_webp(image, quality=85)

        assert isinstance(webp_bytes, bytes)
        assert len(webp_bytes) > 0

        # Можем сохранить через save_image
        output_file = output_dir / "diagram_from_image.webp"
        result = save_image(image, output_file, format="webp")

        assert result["success"] is True
        assert output_file.exists()
        assert result["format"] == "webp"

    def test_render_to_image_without_theme(self, test_plantuml_code):
        """Тест рендеринга без темы."""
        image = render_diagram_to_image(
            diagram_code=test_plantuml_code,
            format="png",
            theme_name=None,
            scale_factor=1.0,
        )

        assert isinstance(image, Image.Image)

    def test_render_to_image_cyrillic(self):
        """Тест рендеринга кириллицы в PIL Image."""
        code = """
@startuml
Alice -> Bob: Привет!
Bob --> Alice: Здравствуй!
@enduml
"""
        image = render_diagram_to_image(
            diagram_code=code,
            format="png",
            theme_name="default",
            scale_factor=1.0,
        )

        assert isinstance(image, Image.Image)
        assert image.width > 0


class TestScaleFactorIntegration:
    """Интеграционные тесты scale_factor с render_diagram_from_string()."""

    def test_legacy_function_with_scale_factor(self, test_plantuml_code, output_dir):
        """Тест что render_diagram_from_string() поддерживает scale_factor."""
        output_file = output_dir / "diagram_scaled_3x.png"

        result = render_diagram_from_string(
            diagram_code=test_plantuml_code,
            output_path=str(output_file),
            format="png",
            theme_name="default",
            scale_factor=3.0,
        )

        assert result["success"] is True
        assert result["scale_factor"] == 3.0
        assert output_file.exists()

        # Проверяем размер изображения
        loaded = Image.open(output_file)
        assert loaded.width > 500  # Для 3x должно быть большое

    def test_scale_factor_1x_vs_3x_file_sizes(self, test_plantuml_code, output_dir):
        """Тест что 3x генерирует больший файл чем 1x."""
        output_1x = output_dir / "diagram_1x.png"
        output_3x = output_dir / "diagram_3x.png"

        result_1x = render_diagram_from_string(
            diagram_code=test_plantuml_code,
            output_path=str(output_1x),
            format="png",
            scale_factor=1.0,
        )

        result_3x = render_diagram_from_string(
            diagram_code=test_plantuml_code,
            output_path=str(output_3x),
            format="png",
            scale_factor=3.0,
        )

        assert result_1x["success"] is True
        assert result_3x["success"] is True

        # 3x должен быть тяжелее
        assert result_3x["file_size_kb"] > result_1x["file_size_kb"]

        # Проверяем реальные размеры
        img_1x = Image.open(output_1x)
        img_3x = Image.open(output_3x)

        assert img_3x.width > img_1x.width * 2.5
        assert img_3x.height > img_1x.height * 2.5

    def test_extreme_quality_level(self, test_plantuml_code, output_dir):
        """Тест Extreme уровня качества (6.0x масштаб) для Deep Zoom."""
        output_extreme = output_dir / "diagram_extreme.png"

        result = render_diagram_from_string(
            diagram_code=test_plantuml_code,
            output_path=str(output_extreme),
            format="png",
            scale_factor=6.0,  # Extreme: 576 DPI
        )

        assert result["success"] is True
        assert result["output_path"] == str(output_extreme)

        # Проверяем что файл создан
        assert output_extreme.exists()

        # Загружаем изображение для проверки размеров
        img_extreme = Image.open(output_extreme)

        # Extreme (6x) должен давать размер >1600px для профессиональной печати
        assert img_extreme.width >= 1600, (
            f"Extreme качество должно давать ширину >=1600px, получено {img_extreme.width}"
        )
        assert img_extreme.height >= 900, (
            f"Extreme качество должно давать высоту >=900px, получено {img_extreme.height}"
        )

        # Проверяем что размер файла значительно больше чем для Low (1x)
        output_1x = output_dir / "diagram_1x_compare.png"
        result_1x = render_diagram_from_string(
            diagram_code=test_plantuml_code,
            output_path=str(output_1x),
            format="png",
            scale_factor=1.0,
        )

        img_1x = Image.open(output_1x)

        # 6x должен быть ровно в 6 раз больше (с допуском на округление)
        expected_width = img_1x.width * 6
        expected_height = img_1x.height * 6

        assert abs(img_extreme.width - expected_width) <= 5, (
            f"6x width должен быть {expected_width}±5, получено {img_extreme.width}"
        )
        assert abs(img_extreme.height - expected_height) <= 5, (
            f"6x height должен быть {expected_height}±5, получено {img_extreme.height}"
        )

    def test_webp_quality_levels(self, test_plantuml_code, output_dir):
        """Тест всех уровней качества для WebP формата."""
        from src.diagram_renderer import QUALITY_LEVELS

        results = {}

        for level, scale in QUALITY_LEVELS.items():
            output_file = output_dir / f"webp_quality_{level.lower()}.webp"

            result = render_diagram_from_string(
                diagram_code=test_plantuml_code,
                output_path=str(output_file),
                format="webp",
                scale_factor=scale,
            )

            assert result["success"] is True
            assert output_file.exists()

            img = Image.open(output_file)
            results[level] = {
                "width": img.width,
                "height": img.height,
                "scale": scale,
            }

        # Проверяем что каждый уровень больше предыдущего
        low_width = results["Low"]["width"]

        assert results["Medium"]["width"] / low_width >= 1.9, (
            "Medium должен быть ~2x от Low"
        )
        assert results["High"]["width"] / low_width >= 2.9, (
            "High должен быть ~3x от Low"
        )
        assert results["Ultra"]["width"] / low_width >= 3.9, (
            "Ultra должен быть ~4x от Low"
        )
        assert results["Extreme"]["width"] / low_width >= 5.8, (
            "Extreme должен быть ~6x от Low"
        )
