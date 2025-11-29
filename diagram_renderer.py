#!/usr/bin/env python3
"""PlantUML диаграммы рендерер.

Этот модуль отвечает за генерацию диаграмм из PlantUML кода.
Использует PlantUML JAR файл и Java для рендеринга.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Literal

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
    """Проверить наличие Java в системе.

    Returns:
        str: Версия Java

    Raises:
        JavaNotFoundError: Если Java не найдена или версия некорректна

    Example:
        >>> version = ensure_java_environment()
        >>> print(f"Java version: {version}")
        Java version: openjdk 17.0.9
    """
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Java выводит версию в stderr
        version_output = result.stderr or result.stdout

        if not version_output:
            raise JavaNotFoundError("Java установлена, но не удалось определить версию")

        # Извлекаем первую строку с версией
        version_line = version_output.split("\n")[0]

        return version_line.strip()

    except FileNotFoundError:
        raise JavaNotFoundError(
            "Java не найдена в системе. "
            "Установите JRE (Java Runtime Environment) версии 8 или выше.\n"
            "macOS: brew install openjdk\n"
            "Windows: https://adoptium.net/\n"
            "Linux: sudo apt-get install default-jre"
        )
    except subprocess.TimeoutExpired:
        raise JavaNotFoundError("Таймаут при проверке Java. Проверьте установку.")
    except Exception as e:
        raise JavaNotFoundError(f"Ошибка при проверке Java: {str(e)}")


def _prepare_diagram_code(diagram_code: str, theme_path: Path | None = None) -> str:
    """Подготовить код диаграммы с включением темы и принудительной установкой Smetana.

    Args:
        diagram_code: Исходный код PlantUML диаграммы
        theme_path: Путь к файлу темы (.puml)

    Returns:
        str: Код диаграммы с включенной темой и !pragma layout smetana
    """
    lines = diagram_code.strip().split("\n")
    has_startuml = lines[0].strip().startswith("@startuml")

    # Формируем директивы
    directives = []

    # ЖЕСТКО устанавливаем Smetana для всех диаграмм
    directives.append("!pragma layout smetana")

    # Добавляем тему если указана
    if theme_path and theme_path.exists():
        directives.append(f"!include {theme_path.absolute()}")

    if has_startuml:
        # Вставляем директивы после @startuml
        for i, directive in enumerate(directives, 1):
            lines.insert(i, directive)
        return "\n".join(lines)
    else:
        # Добавляем @startuml и директивы в начало
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
    """Сгенерировать диаграмму из PlantUML кода.

    Функция использует subprocess.Popen для передачи кода через stdin,
    что позволяет избежать создания временных файлов.

    Args:
        diagram_code: Исходный код PlantUML диаграммы
        output_path: Абсолютный путь к выходному файлу
        format: Формат выходного файла (png, svg, eps, pdf)
        theme_name: Имя темы из папки asset/themes (без расширения .puml)
                   Или None для отключения темы

    Returns:
        dict: Информация о результате рендеринга:
            - success: bool - успешность операции
            - output_path: str - путь к созданному файлу
            - format: str - формат файла
            - file_size_kb: float - размер файла в КБ
            - java_version: str - версия Java
            - theme_used: str | None - использованная тема

    Raises:
        JavaNotFoundError: Если Java не найдена
        PlantUMLRenderError: Если произошла ошибка рендеринга
        FileNotFoundError: Если PlantUML JAR не найден

    Example:
        >>> result = render_diagram_from_string(
        ...     diagram_code="@startuml\\nAlice -> Bob: Hello\\n@enduml",
        ...     output_path="/tmp/diagram.png",
        ...     format="png",
        ...     theme_name="default"
        ... )
        >>> print(result["success"])
        True
    """
    # Проверка Java
    java_version = ensure_java_environment()

    # Проверка PlantUML JAR
    if not PLANTUML_JAR.exists():
        raise FileNotFoundError(
            f"PlantUML JAR не найден: {PLANTUML_JAR}\n"
            "Запустите скрипт установки или скачайте вручную."
        )

    # Преобразуем путь в Path объект
    output_path = Path(output_path)

    # Создаем директорию если не существует
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Определяем путь к теме
    theme_path = None
    if theme_name:
        theme_path = THEMES_DIR / f"{theme_name}.puml"
        if not theme_path.exists():
            raise FileNotFoundError(
                f"Тема не найдена: {theme_path}\n"
                f"Доступные темы в {THEMES_DIR}: "
                f"{[f.stem for f in THEMES_DIR.glob('*.puml')]}"
            )


def render_diagram_from_string(
    diagram_code: str,
    output_path: str | Path,
    format: DiagramFormat = "png",
    theme_name: str | None = "default",
) -> dict:
    """Сгенерировать диаграмму из PlantUML кода.

    Функция использует subprocess.Popen для передачи кода через stdin,
    что позволяет избежать создания временных файлов.

    Args:
        diagram_code: Исходный код PlantUML диаграммы
        output_path: Абсолютный путь к выходному файлу
        format: Формат выходного файла (png, svg, eps, pdf)
        theme_name: Имя темы из папки asset/themes (без расширения .puml)
                   Или None для отключения темы

    Returns:
        dict: Информация о результате рендеринга:
            - success: bool - успешность операции
            - output_path: str - путь к созданному файлу
            - format: str - формат файла
            - file_size_kb: float - размер файла в КБ
            - java_version: str - версия Java
            - theme_used: str | None - использованная тема

    Raises:
        JavaNotFoundError: Если Java не найдена
        PlantUMLSyntaxError: Если PlantUML код содержит синтаксические ошибки
        PlantUMLRenderError: Если произошла ошибка рендеринга
        FileNotFoundError: Если PlantUML JAR не найден

    Example:
        >>> result = render_diagram_from_string(
        ...     diagram_code="@startuml\\nAlice -> Bob: Hello\\n@enduml",
        ...     output_path="/tmp/diagram.png",
        ...     format="png",
        ...     theme_name="default"
        ... )
        >>> print(result["success"])
        True
    """
    # Проверка Java
    java_version = ensure_java_environment()

    # Проверка PlantUML JAR
    if not PLANTUML_JAR.exists():
        raise FileNotFoundError(
            f"PlantUML JAR не найден: {PLANTUML_JAR}\n"
            "Запустите скрипт установки или скачайте вручную."
        )

    # Преобразуем путь в Path объект
    output_path = Path(output_path)

    # Создаем директорию если не существует
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Определяем путь к теме
    theme_path = None
    if theme_name:
        theme_path = THEMES_DIR / f"{theme_name}.puml"
        if not theme_path.exists():
            raise FileNotFoundError(
                f"Тема не найдена: {theme_path}\n"
                f"Доступные темы в {THEMES_DIR}: "
                f"{[f.stem for f in THEMES_DIR.glob('*.puml')]}"
            )

    # Подготавливаем код с темой и Smetana
    prepared_code = _prepare_diagram_code(diagram_code, theme_path)

    # Формируем команду для PlantUML
    # -pipe: читать из stdin, писать в stdout
    # -t<format>: формат вывода
    # -charset UTF-8: кодировка
    # -Dplantuml.include.path: путь для поиска !include файлов
    # -Dfile.encoding=UTF-8: кодировка файлов
    # -Dplantuml.smetana=true: использовать встроенный Smetana вместо Graphviz
    # -Dplantuml.graphviz.use=false: ЖЕСТКО отключить Graphviz
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
        # Запускаем процесс
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Передаем код через stdin и получаем результат
        stdout_data, stderr_data = process.communicate(
            input=prepared_code.encode("utf-8"), timeout=30
        )

        # Проверяем stderr на ошибки
        stderr_text = stderr_data.decode("utf-8", errors="replace").strip()

        # PlantUML выводит некоторые предупреждения в stderr, которые не критичны
        # Проверяем на критичные ошибки
        if stderr_text and any(
            err in stderr_text.lower()
            for err in ["error", "syntax error", "cannot find", "exception"]
        ):
            # Это может быть синтаксическая ошибка
            raise PlantUMLSyntaxError(f"PlantUML обнаружил ошибку:\n{stderr_text}")

        # Проверяем код возврата
        if process.returncode != 0:
            error_message = stderr_text or "Unknown error"
            raise PlantUMLRenderError(
                f"PlantUML вернул ошибку (код {process.returncode}):\n{error_message}"
            )

        # Проверяем что вывод не пустой
        if len(stdout_data) < 100:
            # Слишком маленький файл - возможно ошибка
            raise PlantUMLRenderError(
                f"PlantUML создал слишком маленький файл ({len(stdout_data)} bytes). "
                "Возможно, в коде есть ошибки."
            )

        # Записываем результат в файл
        with open(output_path, "wb") as f:
            f.write(stdout_data)

        # Получаем размер файла
        file_size = output_path.stat().st_size

        return {
            "success": True,
            "output_path": str(output_path.absolute()),
            "format": format,
            "file_size_kb": round(file_size / 1024, 2),
            "java_version": java_version,
            "theme_used": theme_name,
        }

    except subprocess.TimeoutExpired:
        process.kill()
        raise PlantUMLRenderError(
            "Таймаут при рендеринге диаграммы (30 секунд). "
            "Возможно, диаграмма слишком сложная."
        )
    except (PlantUMLSyntaxError, PlantUMLRenderError):
        # Пробрасываем наши исключения дальше
        raise
    except Exception as e:
        raise PlantUMLRenderError(f"Ошибка при рендеринге диаграммы: {str(e)}")
    # -pipe: читать из stdin, писать в stdout
    # -t<format>: формат вывода
    # -charset UTF-8: кодировка
    # -Dplantuml.include.path: путь для поиска !include файлов
    # -Dfile.encoding=UTF-8: кодировка файлов
    # -Dplantuml.smetana=true: использовать встроенный Smetana вместо Graphviz
    command = [
        "java",
        "-Dfile.encoding=UTF-8",
        "-Dplantuml.include.path=" + str(THEMES_DIR.absolute()),
        "-Dplantuml.smetana=true",
        "-jar",
        str(PLANTUML_JAR.absolute()),
        "-pipe",
        f"-t{format}",
        "-charset",
        "UTF-8",
    ]

    try:
        # Запускаем процесс
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Передаем код через stdin и получаем результат
        stdout_data, stderr_data = process.communicate(
            input=prepared_code.encode("utf-8"), timeout=30
        )

        # Проверяем код возврата
        if process.returncode != 0:
            error_message = stderr_data.decode("utf-8", errors="replace")
            raise PlantUMLRenderError(
                f"PlantUML вернул ошибку (код {process.returncode}):\n{error_message}"
            )

        # Записываем результат в файл
        with open(output_path, "wb") as f:
            f.write(stdout_data)

        # Получаем размер файла
        file_size = output_path.stat().st_size

        return {
            "success": True,
            "output_path": str(output_path.absolute()),
            "format": format,
            "file_size_kb": round(file_size / 1024, 2),
            "java_version": java_version,
            "theme_used": theme_name,
        }

    except subprocess.TimeoutExpired:
        process.kill()
        raise PlantUMLRenderError(
            "Таймаут при рендеринге диаграммы (30 секунд). "
            "Возможно, диаграмма слишком сложная."
        )
    except Exception as e:
        raise PlantUMLRenderError(f"Ошибка при рендеринге диаграммы: {str(e)}")


if __name__ == "__main__":
    # Простой тест
    print("=== PlantUML Renderer Test ===")

    try:
        # Проверка Java
        java_version = ensure_java_environment()
        print(f"✓ Java найдена: {java_version}")

        # Проверка PlantUML JAR
        if PLANTUML_JAR.exists():
            print(f"✓ PlantUML JAR найден: {PLANTUML_JAR}")
        else:
            print(f"✗ PlantUML JAR не найден: {PLANTUML_JAR}")
            sys.exit(1)

        # Проверка тем
        themes = list(THEMES_DIR.glob("*.puml"))
        print(f"✓ Найдено тем: {len(themes)}")
        for theme in themes:
            print(f"  - {theme.stem}")

        # Тестовый рендеринг
        test_code = """
@startuml
Alice -> Bob: Authentication Request
Bob --> Alice: Authentication Response

Alice -> Bob: Another authentication Request
Alice <-- Bob: Another authentication Response
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
