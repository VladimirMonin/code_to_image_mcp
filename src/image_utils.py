"""Утилиты для обработки изображений.

Модуль отвечает за универсальную обработку изображений:
сохранение, конвертацию форматов, масштабирование.

Принцип: модуль не знает об источнике изображения (код/диаграмма),
он работает только с пикселями (Pillow Image объектами).

Функции:
    save_image(image, output_path, format, quality) -> dict
        Сохраняет изображение в указанном формате с оптимизацией.
    resize_image(image, scale_factor) -> Image
        Умное масштабирование с качественным фильтром Lanczos.
    convert_to_webp(image, quality) -> bytes
        Конвертирует изображение в WebP с сжатием.
"""

import logging
from pathlib import Path
from typing import Literal
from io import BytesIO

from PIL import Image

logger = logging.getLogger(__name__)

# Поддерживаемые форматы
ImageFormat = Literal["webp", "png", "jpeg", "jpg"]

# Настройки сжатия по умолчанию
DEFAULT_QUALITY = {
    "webp": 90,  # Баланс качество/размер для WebP
    "jpeg": 92,  # Высокое качество для JPEG
    "jpg": 92,
    "png": None,  # PNG без потерь, но с optimize=True
}


class ImageProcessingError(Exception):
    """Ошибка обработки изображения."""

    pass


def save_image(
    image: Image.Image,
    output_path: str | Path,
    format: ImageFormat = "webp",
    quality: int | None = None,
) -> dict:
    """Сохраняет изображение в указанном формате с оптимизацией.

    Args:
        image: Объект изображения Pillow.
        output_path: Путь для сохранения файла.
        format: Формат файла (webp, png, jpeg).
        quality: Качество сжатия (1-100). Если None, используется DEFAULT_QUALITY.

    Returns:
        Словарь с информацией о сохранении:
            {
                "success": bool,
                "path": str,
                "format": str,
                "size_bytes": int,
                "dimensions": tuple[int, int]
            }

    Raises:
        ImageProcessingError: Если сохранение не удалось.
    """
    output_path = Path(output_path)
    format_lower = format.lower()

    # Используем качество по умолчанию если не указано
    if quality is None:
        quality = DEFAULT_QUALITY.get(format_lower)

    # Создаем директорию если не существует
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.debug(
        f"💾 Сохранение изображения: {output_path.name} (формат={format_lower})"
    )

    try:
        # Параметры сохранения в зависимости от формата
        save_kwargs = {}

        if format_lower == "webp":
            # WebP с оптимизацией и методом 6 (лучшее сжатие)
            save_kwargs = {
                "format": "WEBP",
                "quality": quality,
                "method": 6,  # Максимальное качество сжатия (медленнее, но лучше)
            }
            logger.debug(f"🎨 WebP параметры: quality={quality}, method=6")

        elif format_lower == "png":
            # PNG без потерь, но с оптимизацией
            save_kwargs = {
                "format": "PNG",
                "optimize": True,  # Оптимизация размера без потери качества
                "compress_level": 6,  # Уровень сжатия zlib (0-9)
            }
            logger.debug(f"🎨 PNG параметры: optimize=True, compress_level=6")

        elif format_lower in ("jpeg", "jpg"):
            # JPEG с конвертацией в RGB если нужно
            if image.mode in ("RGBA", "LA", "P"):
                # Конвертируем в RGB для JPEG (не поддерживает прозрачность)
                rgb_image = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                rgb_image.paste(
                    image, mask=image.split()[-1] if image.mode == "RGBA" else None
                )
                image = rgb_image
                logger.debug("🔄 Конвертация RGBA -> RGB для JPEG")

            save_kwargs = {
                "format": "JPEG",
                "quality": quality,
                "optimize": True,
                "progressive": True,  # Прогрессивная загрузка
            }
            logger.debug(f"🎨 JPEG параметры: quality={quality}, progressive=True")

        else:
            raise ImageProcessingError(
                f"Неподдерживаемый формат: {format_lower}. "
                f"Доступные: {', '.join(DEFAULT_QUALITY.keys())}"
            )

        # Сохраняем изображение
        image.save(output_path, **save_kwargs)

        # Получаем размер файла
        file_size = output_path.stat().st_size
        size_kb = file_size / 1024

        logger.info(
            f"💾 Изображение сохранено: {output_path.name} "
            f"({image.width}x{image.height}, {size_kb:.2f} KB)"
        )

        return {
            "success": True,
            "path": str(output_path.absolute()),
            "format": format_lower,
            "size_bytes": file_size,
            "dimensions": (image.width, image.height),
        }

    except Exception as e:
        error_msg = f"Ошибка сохранения изображения: {e}"
        logger.error(f"❌ {error_msg}")
        raise ImageProcessingError(error_msg) from e


def resize_image(
    image: Image.Image,
    scale_factor: float = 1.0,
) -> Image.Image:
    """Умное масштабирование изображения с качественным фильтром.

    Args:
        image: Объект изображения Pillow.
        scale_factor: Коэффициент масштабирования (1.0 = оригинальный размер).

    Returns:
        Новое изображение с измененным размером.

    Raises:
        ImageProcessingError: Если масштабирование не удалось.
    """
    if scale_factor <= 0:
        raise ImageProcessingError(f"Некорректный scale_factor: {scale_factor}")

    if scale_factor == 1.0:
        logger.debug("⏭️  Масштабирование не требуется (scale_factor=1.0)")
        return image

    try:
        original_size = image.size
        new_width = int(image.width * scale_factor)
        new_height = int(image.height * scale_factor)

        logger.debug(
            f"🖼️  Масштабирование: {original_size[0]}x{original_size[1]} -> "
            f"{new_width}x{new_height} (×{scale_factor})"
        )

        # Используем Lanczos для наилучшего качества при ресайзе
        resized = image.resize(
            (new_width, new_height),
            resample=Image.Resampling.LANCZOS,
        )

        logger.info(f"✅ Изображение масштабировано: {new_width}x{new_height}")

        return resized

    except Exception as e:
        error_msg = f"Ошибка масштабирования изображения: {e}"
        logger.error(f"❌ {error_msg}")
        raise ImageProcessingError(error_msg) from e


def convert_to_webp(
    image: Image.Image,
    quality: int = 90,
) -> bytes:
    """Конвертирует изображение в WebP формат с сжатием.

    Args:
        image: Объект изображения Pillow.
        quality: Качество сжатия (1-100).

    Returns:
        Байты изображения в формате WebP.

    Raises:
        ImageProcessingError: Если конвертация не удалась.
    """
    try:
        logger.debug(f"🔄 Конвертация в WebP (quality={quality})")

        buffer = BytesIO()
        image.save(
            buffer,
            format="WEBP",
            quality=quality,
            method=6,  # Максимальное качество сжатия
        )

        webp_bytes = buffer.getvalue()
        size_kb = len(webp_bytes) / 1024

        logger.info(f"✅ Конвертация в WebP завершена ({size_kb:.2f} KB)")

        return webp_bytes

    except Exception as e:
        error_msg = f"Ошибка конвертации в WebP: {e}"
        logger.error(f"❌ {error_msg}")
        raise ImageProcessingError(error_msg) from e


def load_image_from_bytes(
    image_bytes: bytes,
    source_format: str | None = None,
) -> Image.Image:
    """Загружает изображение из байтов.

    Args:
        image_bytes: Байты изображения.
        source_format: Формат источника (опционально, для логирования).

    Returns:
        Объект изображения Pillow.

    Raises:
        ImageProcessingError: Если загрузка не удалась.
    """
    try:
        logger.debug(
            f"📂 Загрузка изображения из байтов "
            f"({len(image_bytes)} bytes{f', format={source_format}' if source_format else ''})"
        )

        buffer = BytesIO(image_bytes)
        image = Image.open(buffer)

        logger.debug(
            f"✅ Изображение загружено: {image.width}x{image.height}, mode={image.mode}"
        )

        return image

    except Exception as e:
        error_msg = f"Ошибка загрузки изображения из байтов: {e}"
        logger.error(f"❌ {error_msg}")
        raise ImageProcessingError(error_msg) from e
