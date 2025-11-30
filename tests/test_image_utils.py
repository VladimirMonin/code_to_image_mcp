"""Тесты для модуля image_utils.

Проверяет функции:
- save_image() - сохранение изображений в разных форматах
- resize_image() - изменение размера изображений
- convert_to_webp() - конверсия в WebP
- load_image_from_bytes() - загрузка изображений из байтов
"""

import io
from pathlib import Path

import pytest
from PIL import Image

from image_utils import (
    ImageProcessingError,
    convert_to_webp,
    load_image_from_bytes,
    resize_image,
    save_image,
)


@pytest.fixture
def test_image():
    """Создаёт тестовое RGB изображение 100x100."""
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    return img


@pytest.fixture
def test_image_rgba():
    """Создаёт тестовое RGBA изображение с прозрачностью."""
    img = Image.new("RGBA", (100, 100), color=(0, 255, 0, 128))
    return img


@pytest.fixture
def output_dir(tmp_path):
    """Создаёт временную директорию для выходных файлов."""
    output = tmp_path / "output"
    output.mkdir()
    return output


class TestSaveImage:
    """Тесты для функции save_image."""

    def test_save_image_webp(self, test_image, output_dir):
        """Тест сохранения в формате WebP."""
        output_path = output_dir / "test.webp"
        result = save_image(test_image, output_path, format="webp")

        assert result["success"] is True
        assert Path(result["path"]).exists()
        assert result["format"] == "webp"
        assert result["dimensions"] == (100, 100)
        assert result["size_bytes"] > 0

        # Проверяем, что файл читается
        loaded = Image.open(output_path)
        assert loaded.size == (100, 100)

    def test_save_image_png(self, test_image, output_dir):
        """Тест сохранения в формате PNG."""
        output_path = output_dir / "test.png"
        result = save_image(test_image, output_path, format="png")

        assert result["success"] is True
        assert result["format"] == "png"
        assert Path(result["path"]).exists()

    def test_save_image_jpeg(self, test_image, output_dir):
        """Тест сохранения в формате JPEG."""
        output_path = output_dir / "test.jpg"
        result = save_image(test_image, output_path, format="jpeg")

        assert result["success"] is True
        assert result["format"] == "jpeg"
        assert Path(result["path"]).exists()

    def test_save_image_custom_quality(self, test_image, output_dir):
        """Тест сохранения с пользовательским качеством."""
        output_path = output_dir / "test_quality.webp"
        result = save_image(test_image, output_path, format="webp", quality=50)

        assert result["success"] is True
        # Низкое качество должно давать меньший размер
        assert result["size_bytes"] > 0

    def test_save_image_creates_directory(self, test_image, tmp_path):
        """Тест автоматического создания директорий."""
        output_path = tmp_path / "nested" / "deep" / "test.png"
        result = save_image(test_image, output_path, format="png")

        assert result["success"] is True
        assert output_path.exists()

    def test_save_image_rgba_to_jpeg(self, test_image_rgba, output_dir):
        """Тест конверсии RGBA в JPEG (должна конвертировать в RGB)."""
        output_path = output_dir / "test_rgba.jpg"
        result = save_image(test_image_rgba, output_path, format="jpeg")

        assert result["success"] is True
        # JPEG не поддерживает прозрачность, должна быть конверсия
        loaded = Image.open(output_path)
        assert loaded.mode == "RGB"


class TestResizeImage:
    """Тесты для функции resize_image."""

    def test_resize_image_downscale(self, test_image):
        """Тест уменьшения изображения."""
        resized = resize_image(test_image, scale_factor=0.5)

        assert resized.size == (50, 50)
        assert resized.mode == test_image.mode

    def test_resize_image_upscale(self, test_image):
        """Тест увеличения изображения."""
        resized = resize_image(test_image, scale_factor=2.0)

        assert resized.size == (200, 200)

    def test_resize_image_aspect_ratio(self):
        """Тест сохранения пропорций при изменении размера."""
        img = Image.new("RGB", (200, 100), color=(0, 0, 255))
        resized = resize_image(img, scale_factor=0.5)

        assert resized.size == (100, 50)  # Пропорция 2:1 сохранена

    def test_resize_image_same_size(self, test_image):
        """Тест изменения на тот же размер (не должно ничего делать)."""
        resized = resize_image(test_image, scale_factor=1.0)

        # Должен вернуть то же изображение (не создавать новое при scale=1.0)
        assert resized.size == test_image.size
        assert resized is test_image  # Тот же объект при scale=1.0

    def test_resize_image_preserve_mode(self):
        """Тест сохранения режима изображения."""
        rgba_img = Image.new("RGBA", (100, 100), color=(255, 255, 255, 128))
        resized = resize_image(rgba_img, scale_factor=0.5)

        assert resized.mode == "RGBA"


class TestConvertToWebP:
    """Тесты для функции convert_to_webp."""

    def test_convert_to_webp_rgb(self, test_image):
        """Тест конверсии RGB изображения в WebP."""
        webp_bytes = convert_to_webp(test_image)

        assert isinstance(webp_bytes, bytes)
        assert len(webp_bytes) > 0

        # Проверяем, что можно загрузить обратно
        loaded = Image.open(io.BytesIO(webp_bytes))
        assert loaded.format == "WEBP"
        assert loaded.size == test_image.size

    def test_convert_to_webp_rgba(self, test_image_rgba):
        """Тест конверсии RGBA изображения в WebP."""
        webp_bytes = convert_to_webp(test_image_rgba)

        assert isinstance(webp_bytes, bytes)
        assert len(webp_bytes) > 0

        loaded = Image.open(io.BytesIO(webp_bytes))
        assert loaded.mode in ("RGBA", "RGB")  # WebP может сохранять альфа-канал

    def test_convert_to_webp_custom_quality(self, test_image):
        """Тест конверсии с пользовательским качеством."""
        # Создаём более сложное изображение для лучшего тестирования сжатия
        complex_img = Image.new("RGB", (500, 500))
        pixels = complex_img.load()
        for i in range(500):
            for j in range(500):
                pixels[i, j] = (i % 256, j % 256, (i + j) % 256)

        webp_low = convert_to_webp(complex_img, quality=50)
        webp_high = convert_to_webp(complex_img, quality=95)

        assert isinstance(webp_low, bytes)
        assert isinstance(webp_high, bytes)

        # На сложном изображении низкое качество должно давать меньший размер
        assert len(webp_low) < len(webp_high)


class TestLoadImageFromBytes:
    """Тесты для функции load_image_from_bytes."""

    def test_load_image_from_bytes_png(self, test_image):
        """Тест загрузки PNG изображения из байтов."""
        # Конвертируем изображение в байты
        buffer = io.BytesIO()
        test_image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        # Загружаем обратно
        loaded = load_image_from_bytes(image_bytes, source_format="png")

        assert loaded.size == test_image.size
        assert loaded.mode == test_image.mode

    def test_load_image_from_bytes_jpeg(self, test_image):
        """Тест загрузки JPEG изображения из байтов."""
        buffer = io.BytesIO()
        test_image.save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()

        loaded = load_image_from_bytes(image_bytes, source_format="jpeg")

        assert loaded.size == test_image.size
        # JPEG всегда RGB
        assert loaded.mode == "RGB"

    def test_load_image_from_bytes_webp(self, test_image):
        """Тест загрузки WebP изображения из байтов."""
        buffer = io.BytesIO()
        test_image.save(buffer, format="WEBP")
        image_bytes = buffer.getvalue()

        loaded = load_image_from_bytes(image_bytes, source_format="webp")

        assert loaded.size == test_image.size

    def test_load_image_from_bytes_invalid(self):
        """Тест загрузки невалидных байтов."""
        invalid_bytes = b"not an image"

        with pytest.raises(ImageProcessingError):
            load_image_from_bytes(invalid_bytes, source_format="png")

    def test_load_image_from_bytes_empty(self):
        """Тест загрузки пустых байтов."""
        with pytest.raises(ImageProcessingError):
            load_image_from_bytes(b"", source_format="png")


class TestIntegration:
    """Интеграционные тесты для комбинации функций."""

    def test_save_resize_load_cycle(self, test_image, output_dir):
        """Тест цикла: сохранить → изменить размер → загрузить."""
        # Сохраняем
        output_path = output_dir / "cycle.webp"
        save_result = save_image(test_image, output_path, format="webp")
        assert save_result["success"] is True

        # Загружаем
        loaded = Image.open(output_path)

        # Изменяем размер
        resized = resize_image(loaded, scale_factor=0.5)
        assert resized.size == (50, 50)

        # Сохраняем снова
        output_path_resized = output_dir / "cycle_resized.webp"
        save_result2 = save_image(resized, output_path_resized, format="webp")
        assert save_result2["success"] is True
        assert save_result2["dimensions"] == (50, 50)

    def test_convert_multiple_formats(self, test_image, output_dir):
        """Тест конверсии между форматами."""
        # PNG → WebP
        png_path = output_dir / "source.png"
        save_image(test_image, png_path, format="png")

        loaded_png = Image.open(png_path)
        webp_bytes = convert_to_webp(loaded_png)

        # Проверяем WebP
        loaded_webp = Image.open(io.BytesIO(webp_bytes))
        assert loaded_webp.size == test_image.size
        assert loaded_webp.format == "WEBP"

    def test_bytes_to_file_workflow(self, test_image, output_dir):
        """Тест работы с байтами → файл."""
        # Изображение → байты
        buffer = io.BytesIO()
        test_image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        # Байты → PIL Image
        loaded = load_image_from_bytes(image_bytes, source_format="png")

        # PIL Image → WebP bytes
        webp_bytes = convert_to_webp(loaded)

        assert isinstance(webp_bytes, bytes)
        assert len(webp_bytes) > 0

        # Можем снова загрузить
        final = Image.open(io.BytesIO(webp_bytes))
        assert final.size == test_image.size


class TestErrorHandling:
    """Тесты обработки ошибок."""

    def test_save_image_invalid_format(self, test_image, output_dir):
        """Тест сохранения в невалидном формате."""
        output_path = output_dir / "test.invalid"

        with pytest.raises(ImageProcessingError):
            save_image(test_image, output_path, format="invalid_format")  # type: ignore

    def test_resize_image_zero_width(self, test_image):
        """Тест изменения размера на нулевой scale_factor."""
        with pytest.raises(ImageProcessingError):
            resize_image(test_image, scale_factor=0)

    def test_resize_image_negative_width(self, test_image):
        """Тест изменения размера на отрицательный scale_factor."""
        with pytest.raises(ImageProcessingError):
            resize_image(test_image, scale_factor=-0.5)
