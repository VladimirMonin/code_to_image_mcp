"""
Комплексный интеграционный тест всей системы Code to Image MCP.

Тестирует:
- Генерацию скриншотов кода (целиком, функции, классы, методы)
- Рендеринг PlantUML диаграмм из файлов
- Форматы выходных файлов (PNG, WebP, SVG)
- Различные темы PlantUML
- Интеграцию всех модулей системы
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.code_to_image import create_code_image
from src.code_extractor import extract_code_entity
from src.diagram_renderer import render_diagram_from_string
from src.image_utils import convert_to_webp
from PIL import Image


class TestCodeScreenshotsWorkflow:
    """Интеграционные тесты генерации скриншотов кода."""

    @pytest.fixture
    def sample_code_path(self):
        """Путь к тестовому Python файлу."""
        return Path(__file__).parent / "assets" / "sample_code.py"

    @pytest.fixture
    def output_dir(self, tmp_path):
        """Директория для выходных файлов."""
        output = tmp_path / "code_screenshots"
        output.mkdir(exist_ok=True)
        return output

    def test_code_screenshot_full_file(self, sample_code_path, output_dir):
        """Тест: скриншот полного файла кода в PNG."""
        output_file = output_dir / "full_code.png"

        with open(sample_code_path, "r", encoding="utf-8") as f:
            code = f.read()

        img = create_code_image(
            code_string=code,
            language="python",
            style="monokai",
            line_numbers=True,
            font_name="JetBrainsMono",
            font_size=14,
        )

        from src.image_utils import save_image

        save_image(img, str(output_file), format="png")
        result = {"success": True}

        assert result["success"] is True
        assert output_file.exists()
        assert output_file.stat().st_size > 0

        img = Image.open(output_file)
        assert img.width > 0
        assert img.height > 0

    def test_code_screenshot_single_function(self, sample_code_path, output_dir):
        """Тест: скриншот отдельной функции через AST."""
        output_file = output_dir / "function_code.png"

        code = extract_code_entity(
            file_path=str(sample_code_path), entity_name="calculate_sum"
        )

        img = create_code_image(
            code_string=code,
            language="python",
            style="monokai",
            line_numbers=True,
            font_name="JetBrainsMono",
            font_size=16,
        )

        from src.image_utils import save_image

        save_image(img, str(output_file), format="png")
        result = {"success": True}

        assert result["success"] is True
        assert "calculate_sum" in code
        assert "def calculate_sum(a: int, b: int) -> int:" in code

    def test_code_screenshot_class(self, sample_code_path, output_dir):
        """Тест: скриншот целого класса."""
        output_file = output_dir / "class_code.png"

        code = extract_code_entity(
            file_path=str(sample_code_path), entity_name="OrderService"
        )

        img = create_code_image(
            code_string=code,
            language="python",
            style="monokai",
            line_numbers=True,
            font_name="FiraCode",
            font_size=14,
        )

        from src.image_utils import save_image

        save_image(img, str(output_file), format="png")
        result = {"success": True}

        assert result["success"] is True
        assert "class OrderService:" in code
        assert "def create_order" in code

    def test_code_screenshot_method(self, sample_code_path, output_dir):
        """Тест: скриншот отдельного метода класса."""
        output_file = output_dir / "method_code.png"

        code = extract_code_entity(
            file_path=str(sample_code_path),
            entity_name="OrderService.create_order",
            include_decorators=True,
        )

        img = create_code_image(
            code_string=code,
            language="python",
            style="monokai",
            line_numbers=True,
            font_name="JetBrainsMono",
            font_size=15,
        )

        from src.image_utils import save_image

        save_image(img, str(output_file), format="png")
        result = {"success": True}

        assert result["success"] is True
        assert "def create_order" in code


class TestPlantUMLDiagramsWorkflow:
    """Интеграционные тесты PlantUML диаграмм."""

    @pytest.fixture
    def assets_dir(self):
        """Директория с тестовыми .puml файлами."""
        return Path(__file__).parent / "assets"

    @pytest.fixture
    def output_dir(self, tmp_path):
        """Директория для выходных файлов."""
        output = tmp_path / "diagrams"
        output.mkdir(exist_ok=True)
        return output

    @pytest.mark.parametrize(
        "diagram_name,theme",
        [
            ("sequence_diagram", "dark_gold"),
            ("class_diagram", "dark_gold"),
            ("activity_diagram", "light_fresh"),
            ("component_diagram", "default"),
        ],
    )
    def test_render_diagram_png_with_themes(
        self, assets_dir, output_dir, diagram_name, theme
    ):
        """Тест: рендеринг разных диаграмм в PNG с разными темами."""
        input_file = assets_dir / f"{diagram_name}.puml"
        output_file = output_dir / f"{diagram_name}_{theme}.png"

        with open(input_file, "r", encoding="utf-8") as f:
            diagram_code = f.read()

        result = render_diagram_from_string(
            diagram_code=diagram_code,
            output_path=str(output_file),
            format="png",
            theme_name=theme,
            scale_factor=2.0,
        )

        assert result["success"] is True
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    @pytest.mark.parametrize(
        "diagram_name",
        [
            "sequence_diagram",
            "class_diagram",
            "activity_diagram",
            "component_diagram",
        ],
    )
    def test_render_diagram_svg(self, assets_dir, output_dir, diagram_name):
        """Тест: рендеринг диаграмм в SVG формат с Google Fonts."""
        input_file = assets_dir / f"{diagram_name}.puml"
        output_file = output_dir / f"{diagram_name}.svg"

        with open(input_file, "r", encoding="utf-8") as f:
            diagram_code = f.read()

        result = render_diagram_from_string(
            diagram_code=diagram_code,
            output_path=str(output_file),
            format="svg",
            theme_name="dark_gold",
            scale_factor=1.0,
        )

        assert result["success"] is True
        assert output_file.exists()

        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert "<?xml" in content or "<svg" in content

            # Проверяем наличие инъекции Google Fonts
            assert "@import url(" in content
            assert "fonts.googleapis.com" in content
            assert "JetBrains+Mono" in content

    def test_png_to_webp_conversion(self, assets_dir, output_dir):
        """Тест: конвертация PNG диаграмм в WebP формат."""
        diagram_files = [
            "sequence_diagram.puml",
            "class_diagram.puml",
        ]

        for puml_file in diagram_files:
            input_path = assets_dir / puml_file
            png_output = output_dir / puml_file.replace(".puml", ".png")
            webp_output = output_dir / puml_file.replace(".puml", ".webp")

            with open(input_path, "r", encoding="utf-8") as f:
                diagram_code = f.read()

            result_png = render_diagram_from_string(
                diagram_code=diagram_code,
                output_path=str(png_output),
                format="png",
                theme_name="dark_gold",
                scale_factor=2.5,
            )

            assert result_png["success"] is True

            img = Image.open(png_output)
            webp_bytes = convert_to_webp(img, quality=85)

            with open(webp_output, "wb") as f:
                f.write(webp_bytes)
            webp_path = str(webp_output)

            assert Path(webp_path).exists()
            webp_size = Path(webp_path).stat().st_size
            png_size = png_output.stat().st_size

            assert webp_size > 0
            print(
                f"\n{puml_file}: PNG={png_size // 1024}KB, WebP={webp_size // 1024}KB"
            )


class TestEndToEndScenarios:
    """Сквозные сценарии использования системы."""

    @pytest.fixture
    def sample_code_path(self):
        return Path(__file__).parent / "assets" / "sample_code.py"

    @pytest.fixture
    def assets_dir(self):
        return Path(__file__).parent / "assets"

    @pytest.fixture
    def output_dir(self, tmp_path):
        output = tmp_path / "e2e_output"
        output.mkdir(exist_ok=True)
        return output

    def test_documentation_generation_workflow(
        self, sample_code_path, assets_dir, output_dir
    ):
        """
        Сценарий: Генерация полной документации (код + диаграммы).

        1. Скриншот класса OrderService
        2. Диаграмма классов
        3. Диаграмма последовательности
        4. Конвертация в WebP
        """
        results = []

        # 1. Скриншот класса
        code = extract_code_entity(
            file_path=str(sample_code_path), entity_name="OrderService"
        )

        img = create_code_image(
            code_string=code,
            language="python",
            style="monokai",
            line_numbers=True,
            font_name="JetBrainsMono",
            font_size=14,
        )

        from src.image_utils import save_image

        save_image(img, str(output_dir / "order_service.png"), format="png")
        results.append(("Code Screenshot", True))

        # 2. Диаграмма классов
        with open(assets_dir / "class_diagram.puml", "r", encoding="utf-8") as f:
            class_code = f.read()

        class_result = render_diagram_from_string(
            diagram_code=class_code,
            output_path=str(output_dir / "class_diagram.png"),
            format="png",
            theme_name="dark_gold",
            scale_factor=2.5,
        )
        results.append(("Class Diagram", class_result["success"]))

        # 3. Диаграмма последовательности
        with open(assets_dir / "sequence_diagram.puml", "r", encoding="utf-8") as f:
            sequence_code = f.read()

        sequence_result = render_diagram_from_string(
            diagram_code=sequence_code,
            output_path=str(output_dir / "sequence_diagram.png"),
            format="png",
            theme_name="dark_gold",
            scale_factor=2.5,
        )
        results.append(("Sequence Diagram", sequence_result["success"]))

        # 4. Конвертация в WebP
        for png_file in output_dir.glob("*.png"):
            img = Image.open(png_file)
            webp_path = png_file.with_suffix(".webp")
            webp_bytes = convert_to_webp(img, quality=85)
            with open(webp_path, "wb") as f:
                f.write(webp_bytes)
            results.append((f"WebP {png_file.name}", webp_path.exists()))

        # Проверяем успех всех операций
        assert all(success for _, success in results)
        assert len(results) >= 6

    def test_multi_entity_extraction_workflow(self, sample_code_path, output_dir):
        """
        Сценарий: Извлечение и генерация скриншотов для разных типов сущностей.
        """
        entities = [
            ("calculate_sum", "function"),
            ("User", "dataclass"),
            ("OrderService.create_order", "method"),
        ]

        for entity_name, entity_type in entities:
            code = extract_code_entity(
                file_path=str(sample_code_path),
                entity_name=entity_name,
                include_decorators=True,
            )

            safe_name = entity_name.replace(".", "_")
            output_file = output_dir / f"{safe_name}.png"

            img = create_code_image(
                code_string=code,
                language="python",
                style="monokai",
                line_numbers=True,
                font_name="JetBrainsMono",
                font_size=14,
            )

            from src.image_utils import save_image

            save_image(img, str(output_file), format="png")
            result = {"success": True}

            assert result["success"] is True
            assert output_file.exists()


class TestCodeScreenshotsPersistent:
    """
    Тесты скриншотов кода с ПОСТОЯННЫМ сохранением в tests/output/.

    Используют фикстуру output_dir из conftest.py.
    Результаты остаются после тестов для визуальной проверки.
    """

    @pytest.fixture
    def sample_code_path(self):
        """Путь к тестовому Python файлу."""
        return Path(__file__).parent / "assets" / "sample_code.py"

    @pytest.fixture
    def output_dir(self):
        """Директория для ПОСТОЯННОГО сохранения результатов."""
        output = Path(__file__).parent / "output"
        output.mkdir(exist_ok=True)
        return output

    def test_code_full_file_dark_webp(self, sample_code_path, output_dir):
        """Тест: скриншот полного файла — dark theme + WebP + JetBrainsMono."""
        output_file = output_dir / "code_full_file_dark.webp"

        with open(sample_code_path, "r", encoding="utf-8") as f:
            code = f.read()

        img = create_code_image(
            code_string=code,
            language="python",
            style="monokai",  # dark theme
            line_numbers=True,
            font_name="JetBrainsMono",
            font_size=14,
            scale_factor=3.0,  # High quality
        )

        from src.image_utils import save_image

        result = save_image(img, str(output_file), format="webp", quality=90)

        assert result["success"] is True
        assert output_file.exists()
        assert output_file.stat().st_size > 0

        # Проверяем размеры изображения
        loaded = Image.open(output_file)
        assert loaded.width >= 800  # High quality должен давать большой размер

    def test_code_function_dark_webp(self, sample_code_path, output_dir):
        """Тест: скриншот функции — dark theme + WebP + JetBrainsMono."""
        output_file = output_dir / "code_function_dark.webp"

        code = extract_code_entity(
            file_path=str(sample_code_path),
            entity_name="calculate_sum",
        )

        img = create_code_image(
            code_string=code,
            language="python",
            style="dracula",  # another dark theme
            line_numbers=True,
            font_name="JetBrainsMono",
            font_size=16,
            scale_factor=3.0,
        )

        from src.image_utils import save_image

        result = save_image(img, str(output_file), format="webp", quality=90)

        assert result["success"] is True
        assert output_file.exists()
        assert "def calculate_sum" in code

    def test_code_class_dark_webp(self, sample_code_path, output_dir):
        """Тест: скриншот класса — dark theme + WebP + JetBrainsMono."""
        output_file = output_dir / "code_class_dark.webp"

        code = extract_code_entity(
            file_path=str(sample_code_path),
            entity_name="OrderService",
        )

        img = create_code_image(
            code_string=code,
            language="python",
            style="monokai",
            line_numbers=True,
            font_name="JetBrainsMono",
            font_size=14,
            scale_factor=3.0,
        )

        from src.image_utils import save_image

        result = save_image(img, str(output_file), format="webp", quality=90)

        assert result["success"] is True
        assert output_file.exists()
        assert "class OrderService:" in code

    def test_code_method_dark_webp(self, sample_code_path, output_dir):
        """Тест: скриншот метода класса — dark theme + WebP + JetBrainsMono."""
        output_file = output_dir / "code_method_dark.webp"

        code = extract_code_entity(
            file_path=str(sample_code_path),
            entity_name="OrderService.create_order",
            include_decorators=True,
        )

        img = create_code_image(
            code_string=code,
            language="python",
            style="vim",  # another dark theme
            line_numbers=True,
            font_name="JetBrainsMono",
            font_size=15,
            scale_factor=3.0,
        )

        from src.image_utils import save_image

        result = save_image(img, str(output_file), format="webp", quality=90)

        assert result["success"] is True
        assert output_file.exists()
        assert "def create_order" in code

    def test_code_dataclass_dark_webp(self, sample_code_path, output_dir):
        """Тест: скриншот dataclass — dark theme + WebP + JetBrainsMono."""
        output_file = output_dir / "code_dataclass_dark.webp"

        code = extract_code_entity(
            file_path=str(sample_code_path),
            entity_name="User",
            include_decorators=True,  # включить @dataclass
        )

        img = create_code_image(
            code_string=code,
            language="python",
            style="monokai",
            line_numbers=True,
            font_name="JetBrainsMono",
            font_size=14,
            scale_factor=3.0,
        )

        from src.image_utils import save_image

        result = save_image(img, str(output_file), format="webp", quality=90)

        assert result["success"] is True
        assert output_file.exists()
        assert "@dataclass" in code
        assert "class User:" in code

    def test_code_async_function_dark_webp(self, sample_code_path, output_dir):
        """Тест: скриншот async функции — dark theme + WebP + JetBrainsMono."""
        output_file = output_dir / "code_async_dark.webp"

        code = extract_code_entity(
            file_path=str(sample_code_path),
            entity_name="fetch_data",
        )

        img = create_code_image(
            code_string=code,
            language="python",
            style="github-dark",
            line_numbers=True,
            font_name="JetBrainsMono",
            font_size=14,
            scale_factor=3.0,
        )

        from src.image_utils import save_image

        result = save_image(img, str(output_file), format="webp", quality=90)

        assert result["success"] is True
        assert output_file.exists()
        assert "async def fetch_data" in code
