#!/usr/bin/env python3
"""Рендерер PlantUML диаграмм.

Модуль обеспечивает генерацию UML диаграмм из PlantUML кода.
Использует PlantUML JAR файл и Java для рендеринга.

Функции:
    ensure_java_environment() -> str
        Проверяет наличие Java в системе.
    render_diagram_to_image(diagram_code, format, theme_name, scale_factor) -> Image
        Генерирует диаграмму из PlantUML кода и возвращает PIL Image.
    render_diagram_from_string(diagram_code, output_path, format, theme_name, scale_factor) -> dict
        Генерирует диаграмму и сохраняет в файл (legacy, использует image_utils).

Классы:
    JavaNotFoundError
        Исключение при отсутствии Java.
    PlantUMLRenderError
        Ошибка рендеринга PlantUML диаграммы.
    PlantUMLSyntaxError
        Синтаксическая ошибка в PlantUML коде.
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Literal

from PIL import Image

from src.font_initializer import ensure_fonts_initialized
from src.image_utils import save_image, load_image_from_bytes

logger = logging.getLogger(__name__)

# Константы путей
ASSET_DIR = Path(__file__).parent.parent / "asset"
PLANTUML_JAR = ASSET_DIR / "bins" / "plantuml.jar"
THEMES_DIR = ASSET_DIR / "themes"

# Маппинг уровней детализации в коэффициенты масштабирования
# Базовый DPI = 96. Extreme (6.0) дает ~576 DPI для профессиональной печати.
QUALITY_LEVELS = {
    "Low": 1.0,  # 96 DPI (Web preview)
    "Medium": 2.0,  # 192 DPI (Standard screens)
    "High": 3.0,  # 288 DPI (High-res screens / Default)
    "Ultra": 4.0,  # 384 DPI (4K Presentations)
    "Extreme": 6.0,  # 576 DPI (Print / Deep Zoom)
}

# Поддерживаемые форматы
DiagramFormat = Literal["png", "svg", "eps", "pdf"]


class JavaNotFoundError(Exception):
    """Java не найдена в системе."""

    pass


class PlantUMLRenderError(Exception):
    """Ошибка рендеринга PlantUML диаграммы."""

    pass


class PlantUMLSyntaxError(Exception):
    """Синтаксическая ошибка в PlantUML коде."""

    pass


def ensure_java_environment() -> str:
    """Проверяет наличие Java в системе.

    Returns:
        Версия Java.

    Raises:
        JavaNotFoundError: Если Java не найдена или версия некорректна.
    """
    logger.debug("🔍 Проверка Java окружения")
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        version_output = result.stderr or result.stdout

        if not version_output:
            logger.error("❌ Java установлена, но версия не определена")
            raise JavaNotFoundError("Java установлена, но не удалось определить версию")

        version_line = version_output.split("\n")[0].strip()
        logger.info(f"☕ Java обнаружена: {version_line}")

        return version_line

    except FileNotFoundError:
        logger.error("❌ Java не найдена в PATH")
        raise JavaNotFoundError(
            "Java не найдена в системе. "
            "Установите JRE (Java Runtime Environment) версии 8 или выше.\n"
            "macOS: brew install openjdk\n"
            "Windows: https://adoptium.net/\n"
            "Linux: sudo apt-get install default-jre"
        )
    except subprocess.TimeoutExpired:
        logger.error("❌ Таймаут при проверке Java")
        raise JavaNotFoundError("Таймаут при проверке Java. Проверьте установку.")
    except JavaNotFoundError:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке Java: {e}")
        raise JavaNotFoundError(f"Ошибка при проверке Java: {str(e)}")


def _prepare_diagram_code(
    diagram_code: str, theme_path: Path | None = None, dpi: int | None = None
) -> str:
    """Подготавливает код диаграммы с темой, Smetana и DPI.

    Args:
        diagram_code: Исходный код PlantUML диаграммы.
        theme_path: Путь к файлу темы (.puml).
        dpi: DPI для инъекции в код через skinparam (обход ограничения Smetana).

    Returns:
        Код диаграммы с включенной темой, !pragma layout smetana и skinparam dpi.
    """
    lines = diagram_code.strip().split("\n")
    has_startuml = lines[0].strip().startswith("@startuml")

    directives = ["!pragma layout smetana"]

    # HARD INJECTION: Smetana игнорирует флаг -Sdpi, поэтому вшиваем в код
    if dpi and dpi > 96:
        directives.append(f"skinparam dpi {dpi}")
        logger.debug(f"💉 DPI инъекция в PlantUML код: skinparam dpi {dpi}")

    if theme_path and theme_path.exists():
        directives.append(f"!include {theme_path.absolute()}")

    if has_startuml:
        for i, directive in enumerate(directives, 1):
            lines.insert(i, directive)
        return "\n".join(lines)
    else:
        result = "@startuml\n" + "\n".join(directives) + "\n" + diagram_code
        if not diagram_code.strip().endswith("@enduml"):
            result += "\n@enduml"
        return result


def render_diagram_to_image(
    diagram_code: str,
    format: DiagramFormat = "png",
    theme_name: str | None = "default",
    scale_factor: float = 1.0,
) -> Image.Image:
    """Генерирует диаграмму из PlantUML кода и возвращает PIL Image объект.

    Args:
        diagram_code: Исходный код PlantUML диаграммы.
        format: Формат рендеринга (png, svg, eps, pdf, webp).
        theme_name: Имя темы из папки asset/themes или None.
        scale_factor: Коэффициент масштабирования для увеличения разрешения.
                     1.0 = 96 DPI (стандарт), 2.0 = 192 DPI, 3.0 = 288 DPI.

    Returns:
        PIL Image объект.

    Raises:
        JavaNotFoundError: Если Java не найдена.
        PlantUMLSyntaxError: Если PlantUML код содержит синтаксические ошибки.
        PlantUMLRenderError: Если произошла ошибка рендеринга.
    """
    logger.info("📐 Начало рендеринга PlantUML диаграммы")

    # Инициализация шрифтов (выполняется один раз, затем кешируется)
    logger.debug("🔍 Проверка инициализации кастомных шрифтов")
    font_init_result = ensure_fonts_initialized()

    if not font_init_result["success"]:
        logger.error(f"❌ Ошибка инициализации шрифтов: {font_init_result['error']}")
        raise JavaNotFoundError(font_init_result["error"])

    if font_init_result["already_installed"]:
        logger.debug(
            f"✅ Шрифты уже установлены: {len(font_init_result['fonts'])} файлов"
        )
    else:
        logger.info(
            f"💉 Шрифты установлены в JRE: {len(font_init_result['fonts'])} файлов "
            f"({font_init_result['java_home']})"
        )

    java_version = ensure_java_environment()

    if not PLANTUML_JAR.exists():
        logger.error(f"❌ PlantUML JAR не найден: {PLANTUML_JAR}")
        raise FileNotFoundError(
            f"PlantUML JAR не найден: {PLANTUML_JAR}\n"
            "Запустите скрипт установки или скачайте вручную."
        )

    logger.debug(f"📦 PlantUML JAR: {PLANTUML_JAR}")

    # Проверка темы
    theme_path = None
    if theme_name:
        theme_path = THEMES_DIR / f"{theme_name}.puml"
        if not theme_path.exists():
            logger.error(f"❌ Тема не найдена: {theme_path}")
            raise FileNotFoundError(
                f"Тема не найдена: {theme_path}\n"
                f"Доступные темы в {THEMES_DIR}: "
                f"{[f.stem for f in THEMES_DIR.glob('*.puml')]}"
            )
        logger.info(f"🎨 Применение темы: {theme_name}")

    # Вычисляем DPI на основе scale_factor
    # 1.0 = 96 DPI (стандарт), 2.0 = 192 DPI, 3.0 = 288 DPI, 6.0 = 576 DPI
    dpi = int(96 * scale_factor)
    logger.debug(f"📏 Force DPI Injection: {dpi} (Scale: {scale_factor}x)")

    prepared_code = _prepare_diagram_code(diagram_code, theme_path, dpi)

    command = [
        "java",
        "-Dfile.encoding=UTF-8",
        "-Dplantuml.include.path=" + str(THEMES_DIR.absolute()),
        "-Dplantuml.smetana=true",
        "-Dplantuml.graphviz.use=false",
        f"-DPLANTUML_LIMIT_SIZE=16384",  # Увеличиваем лимит для больших изображений
        "-jar",
        str(PLANTUML_JAR.absolute()),
        "-pipe",
        f"-t{format}",
        "-charset",
        "UTF-8",
    ]

    logger.debug(f"⚙️ Запуск Java процесса для PlantUML")

    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout_data, stderr_data = process.communicate(
            input=prepared_code.encode("utf-8"), timeout=30
        )

        stderr_text = stderr_data.decode("utf-8", errors="replace").strip()

        if stderr_text and any(
            err in stderr_text.lower()
            for err in ["error", "syntax error", "cannot find", "exception"]
        ):
            logger.error(f"💥 Синтаксическая ошибка PlantUML: {stderr_text}")
            raise PlantUMLSyntaxError(f"PlantUML обнаружил ошибку:\n{stderr_text}")

        if process.returncode != 0:
            error_message = stderr_text or "Unknown error"
            logger.error(f"❌ PlantUML вернул код ошибки: {process.returncode}")
            raise PlantUMLRenderError(
                f"PlantUML вернул ошибку (код {process.returncode}):\n{error_message}"
            )

        if len(stdout_data) < 100:
            logger.error(
                f"❌ PlantUML создал слишком маленький файл: {len(stdout_data)} bytes"
            )
            raise PlantUMLRenderError(
                f"PlantUML создал слишком маленький файл ({len(stdout_data)} bytes). "
                "Возможно, в коде есть ошибки."
            )

        # Загружаем изображение из байтов только для растровых форматов
        if format == "png":
            image = load_image_from_bytes(stdout_data, source_format=format)

            logger.info(
                f"✅ Диаграмма отрендерена: {image.width}x{image.height}, "
                f"размер данных: {len(stdout_data) / 1024:.2f} KB"
            )

            return image
        else:
            # Для SVG/EPS/PDF возвращаем заглушку (эти форматы не поддерживают PIL Image)
            logger.warning(
                f"⚠️ Формат {format} не поддерживается render_diagram_to_image(). "
                f"Используйте render_diagram_from_string() для векторных форматов."
            )
            raise PlantUMLRenderError(
                f"Формат {format} не поддерживается для возврата PIL Image. "
                "Используйте только 'png' для render_diagram_to_image()."
            )

    except subprocess.TimeoutExpired:
        process.kill()
        logger.error("❌ Таймаут при рендеринге диаграммы (30 секунд)")
        raise PlantUMLRenderError(
            "Таймаут при рендеринге диаграммы (30 секунд). "
            "Возможно, диаграмма слишком сложная."
        )
    except (PlantUMLSyntaxError, PlantUMLRenderError):
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка при рендеринге: {e}")
        raise PlantUMLRenderError(f"Ошибка при рендеринге диаграммы: {str(e)}")


def render_diagram_from_string(
    diagram_code: str,
    output_path: str | Path,
    format: DiagramFormat = "png",
    theme_name: str | None = "default",
    scale_factor: float = 1.0,
) -> dict:
    """Генерирует диаграмму из PlantUML кода и сохраняет в файл.

    LEGACY функция для обратной совместимости. Для PNG использует render_diagram_to_image()
    и image_utils. Для SVG/EPS/PDF сохраняет напрямую.

    Args:
        diagram_code: Исходный код PlantUML диаграммы.
        output_path: Абсолютный путь к выходному файлу.
        format: Формат выходного файла (png, svg, eps, pdf, webp).
        theme_name: Имя темы из папки asset/themes или None.
        scale_factor: Коэффициент масштабирования (1.0 = стандарт, 3.0 = для 4K).
                     Применяется только для PNG.

    Returns:
        Словарь с информацией о результате рендеринга.

    Raises:
        JavaNotFoundError: Если Java не найдена.
        PlantUMLSyntaxError: Если PlantUML код содержит синтаксические ошибки.
        PlantUMLRenderError: Если произошла ошибка рендеринга.
    """
    output_path = Path(output_path)

    # Для PNG/WebP используем новую функцию с PIL Image
    if format in ("png", "webp"):
        # Генерируем изображение через новую функцию
        image = render_diagram_to_image(
            diagram_code=diagram_code,
            format="png",  # PlantUML всегда генерирует PNG, конвертируем потом
            theme_name=theme_name,
            scale_factor=scale_factor,
        )

        # Определяем формат для сохранения (из расширения файла или параметра)
        save_format = output_path.suffix.lstrip(".").lower() or format

        # Сохраняем через image_utils
        save_result = save_image(
            image=image,
            output_path=output_path,
            format=save_format,  # type: ignore
        )

        java_version = ensure_java_environment()

        return {
            "success": True,
            "output_path": save_result["path"],
            "format": save_result["format"],
            "file_size_kb": round(save_result["size_bytes"] / 1024, 2),
            "dimensions": save_result["dimensions"],
            "java_version": java_version,
            "theme_used": theme_name,
            "scale_factor": scale_factor,
        }

    # Для SVG/EPS/PDF используем прямое сохранение
    else:
        # Инициализация шрифтов
        logger.debug("🔍 Проверка инициализации кастомных шрифтов")
        font_init_result = ensure_fonts_initialized()

        if not font_init_result["success"]:
            logger.error(
                f"❌ Ошибка инициализации шрифтов: {font_init_result['error']}"
            )
            raise JavaNotFoundError(font_init_result["error"])

        java_version = ensure_java_environment()

        if not PLANTUML_JAR.exists():
            raise FileNotFoundError(f"PlantUML JAR не найден: {PLANTUML_JAR}")

        # Проверка темы
        theme_path = None
        if theme_name:
            theme_path = THEMES_DIR / f"{theme_name}.puml"
            if not theme_path.exists():
                raise FileNotFoundError(f"Тема не найдена: {theme_path}")

        prepared_code = _prepare_diagram_code(diagram_code, theme_path)

        command = [
            "java",
            "-Dfile.encoding=UTF-8",
            "-Dplantuml.include.path=" + str(THEMES_DIR.absolute()),
            "-Dplantuml.smetana=true",
            "-Dplantuml.graphviz.use=false",
            "-jar",
            str(PLANTUML_JAR.absolute()),
            "-pipe",
            f"-t{format}",
            "-charset",
            "UTF-8",
        ]

        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            stdout_data, stderr_data = process.communicate(
                input=prepared_code.encode("utf-8"), timeout=30
            )

            stderr_text = stderr_data.decode("utf-8", errors="replace").strip()

            if stderr_text and any(
                err in stderr_text.lower()
                for err in ["error", "syntax error", "cannot find", "exception"]
            ):
                raise PlantUMLSyntaxError(f"PlantUML обнаружил ошибку:\n{stderr_text}")

            if process.returncode != 0:
                error_message = stderr_text or "Unknown error"
                raise PlantUMLRenderError(
                    f"PlantUML вернул ошибку (код {process.returncode}):\n{error_message}"
                )

            # Создаём директорию если нужно
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Сохраняем напрямую
            with open(output_path, "wb") as f:
                f.write(stdout_data)

            file_size = len(stdout_data)
            logger.info(
                f"✅ Диаграмма сохранена: {output_path.name}, "
                f"размер: {file_size / 1024:.2f} KB"
            )

            return {
                "success": True,
                "output_path": str(output_path.absolute()),
                "format": format,
                "file_size_kb": round(file_size / 1024, 2),
                "dimensions": None,  # Нет для векторных форматов
                "java_version": java_version,
                "theme_used": theme_name,
                "scale_factor": scale_factor if format == "png" else None,
            }

        except subprocess.TimeoutExpired:
            process.kill()
            raise PlantUMLRenderError(
                "Таймаут при рендеринге диаграммы (30 секунд). "
                "Возможно, диаграмма слишком сложная."
            )
        except (PlantUMLSyntaxError, PlantUMLRenderError):
            raise
        except Exception as e:
            logger.error(f"❌ Ошибка при рендеринге: {e}")
            raise PlantUMLRenderError(f"Ошибка при рендеринге диаграммы: {str(e)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("=== PlantUML Renderer Test ===")

    try:
        java_version = ensure_java_environment()
        print(f"✓ Java найдена: {java_version}")

        if PLANTUML_JAR.exists():
            print(f"✓ PlantUML JAR найден: {PLANTUML_JAR}")
        else:
            print(f"✗ PlantUML JAR не найден: {PLANTUML_JAR}")
            sys.exit(1)

        themes = list(THEMES_DIR.glob("*.puml"))
        print(f"✓ Найдено тем: {len(themes)}")
        for theme in themes:
            print(f"  - {theme.stem}")

        test_code = """
@startuml
Alice -> Bob: Authentication Request
Bob --> Alice: Authentication Response
@enduml
"""
        test_output = Path("tests/output/plantuml_test.png")

        print("\nТестовый рендеринг (1x scale)...")
        result = render_diagram_from_string(
            diagram_code=test_code,
            output_path=test_output,
            format="png",
            theme_name="default",
            scale_factor=1.0,
        )

        print(f"✓ Диаграмма создана: {result['output_path']}")
        print(f"  Размер: {result['file_size_kb']} KB")
        print(f"  Формат: {result['format']}")
        print(f"  Разрешение: {result['dimensions']}")
        print(f"  Масштаб: {result['scale_factor']}x")

        # Тест с высоким разрешением
        test_output_hq = Path("tests/output/plantuml_test_3x.png")
        print("\nТестовый рендеринг (3x scale для 4K)...")
        result_hq = render_diagram_from_string(
            diagram_code=test_code,
            output_path=test_output_hq,
            format="png",
            theme_name="default",
            scale_factor=3.0,
        )

        print(f"✓ Диаграмма HQ создана: {result_hq['output_path']}")
        print(f"  Размер: {result_hq['file_size_kb']} KB")
        print(f"  Разрешение: {result_hq['dimensions']}")
        print(f"  Масштаб: {result_hq['scale_factor']}x")

    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
