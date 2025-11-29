#!/usr/bin/env python3
"""Рендерер PlantUML диаграмм.

Модуль обеспечивает генерацию UML диаграмм из PlantUML кода.
Использует PlantUML JAR файл и Java для рендеринга.

Функции:
    ensure_java_environment() -> str
        Проверяет наличие Java в системе.
    render_diagram_from_string(diagram_code, output_path, format, theme_name) -> dict
        Генерирует диаграмму из PlantUML кода.

Классы:
    JavaNotFoundError
        Исключение при отсутствии Java.
    PlantUMLRenderError
        Исключение при ошибке рендеринга.
    PlantUMLSyntaxError
        Исключение при синтаксической ошибке PlantUML.
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Literal

from font_initializer import ensure_fonts_initialized

logger = logging.getLogger(__name__)

# Константы путей
ASSET_DIR = Path(__file__).parent / "asset"
PLANTUML_JAR = ASSET_DIR / "bins" / "plantuml.jar"
THEMES_DIR = ASSET_DIR / "themes"

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


def _prepare_diagram_code(diagram_code: str, theme_path: Path | None = None) -> str:
    """Подготавливает код диаграммы с темой и Smetana.

    Args:
        diagram_code: Исходный код PlantUML диаграммы.
        theme_path: Путь к файлу темы (.puml).

    Returns:
        Код диаграммы с включенной темой и !pragma layout smetana.
    """
    lines = diagram_code.strip().split("\n")
    has_startuml = lines[0].strip().startswith("@startuml")

    directives = ["!pragma layout smetana"]

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


def render_diagram_from_string(
    diagram_code: str,
    output_path: str | Path,
    format: DiagramFormat = "png",
    theme_name: str | None = "default",
) -> dict:
    """Генерирует диаграмму из PlantUML кода.

    Использует subprocess.Popen для передачи кода через stdin,
    что позволяет избежать создания временных файлов.

    Args:
        diagram_code: Исходный код PlantUML диаграммы.
        output_path: Абсолютный путь к выходному файлу.
        format: Формат выходного файла (png, svg, eps, pdf).
        theme_name: Имя темы из папки asset/themes или None.

    Returns:
        Словарь с информацией о результате рендеринга.

    Raises:
        JavaNotFoundError: Если Java не найдена.
        PlantUMLSyntaxError: Если PlantUML код содержит синтаксические ошибки.
        PlantUMLRenderError: Если произошла ошибка рендеринга.
        FileNotFoundError: Если PlantUML JAR или тема не найдены.
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

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    logger.debug(f"🗂️ Директория вывода: {output_path.parent}")

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

        with open(output_path, "wb") as f:
            f.write(stdout_data)

        file_size = output_path.stat().st_size
        file_size_kb = round(file_size / 1024, 2)

        logger.info(f"💾 Диаграмма сохранена: {output_path}")
        logger.info(f"✅ Рендеринг завершён успешно ({file_size_kb} KB)")

        return {
            "success": True,
            "output_path": str(output_path.absolute()),
            "format": format,
            "file_size_kb": file_size_kb,
            "java_version": java_version,
            "theme_used": theme_name,
        }

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
        test_output = Path("/tmp/plantuml_test.png")

        print("\nТестовый рендеринг...")
        result = render_diagram_from_string(
            diagram_code=test_code,
            output_path=test_output,
            format="png",
            theme_name="default",
        )

        print(f"✓ Диаграмма создана: {result['output_path']}")
        print(f"  Размер: {result['file_size_kb']} KB")
        print(f"  Формат: {result['format']}")
        print(f"  Тема: {result['theme_used']}")

    except Exception as e:
        print(f"✗ Ошибка: {e}")
        sys.exit(1)
