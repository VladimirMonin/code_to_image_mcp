"""Инициализатор шрифтов для PlantUML.

Модуль отвечает за однократную установку кастомных шрифтов в JRE,
чтобы PlantUML мог их использовать.

Стратегия:
1. Проверяем маркер-файл - если установка уже была, пропускаем
2. Находим Java JRE
3. Копируем TTF шрифты в lib/fonts JRE
4. Создаем маркер-файл об успешной установке

Функции:
    ensure_fonts_initialized() -> dict
        Гарантирует, что шрифты установлены в JRE.
"""

import logging
import platform
import shutil
import subprocess
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Константы
FONTS_DIR = Path(__file__).parent / "asset" / "fonts"
MARKER_FILE = Path(__file__).parent / ".fonts_installed.json"


class JavaNotFoundError(Exception):
    """Java не найдена в системе."""

    pass


class FontInitializationError(Exception):
    """Ошибка инициализации шрифтов."""

    pass


def _find_java_home() -> Path:
    """Находит путь к установке Java JRE/JDK.

    Returns:
        Path: Путь к корневой директории Java.

    Raises:
        JavaNotFoundError: Если Java не найдена.
    """
    logger.debug("🔍 Поиск Java установки...")

    try:
        # Пытаемся получить java.home через Java команду
        result = subprocess.run(
            ["java", "-XshowSettings:properties", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Парсим вывод для поиска java.home
        for line in result.stderr.split("\n"):
            if "java.home" in line:
                # Формат: "    java.home = C:\Path\To\Java"
                parts = line.split("=")
                if len(parts) == 2:
                    java_home = Path(parts[1].strip())
                    if java_home.exists():
                        logger.info(f"☕ Найдена Java: {java_home}")
                        return java_home

        # Fallback: пытаемся найти через where/which
        where_cmd = "where" if platform.system() == "Windows" else "which"
        result = subprocess.run([where_cmd, "java"], capture_output=True, text=True)

        if result.returncode == 0:
            java_exe = Path(result.stdout.strip().split("\n")[0])
            # java.exe -> bin -> JRE root
            java_home = java_exe.parent.parent

            # Проверка на java8path (Windows специфика)
            if "java8path" in str(java_home).lower():
                # Это симлинк, ищем реальную установку в Program Files
                if platform.system() == "Windows":
                    # Стандартные пути установки JRE
                    possible_paths = [
                        Path(r"C:\Program Files\Java"),
                        Path(r"C:\Program Files (x86)\Java"),
                    ]

                    for base_path in possible_paths:
                        if base_path.exists():
                            # Ищем последнюю версию JRE/JDK
                            jre_dirs = sorted(base_path.glob("jre*")) + sorted(
                                base_path.glob("jdk*")
                            )
                            if jre_dirs:
                                java_home = jre_dirs[-1]
                                break

            if java_home.exists():
                logger.info(f"☕ Найдена Java: {java_home}")
                return java_home

        raise JavaNotFoundError("Не удалось определить путь к Java")

    except subprocess.TimeoutExpired:
        raise JavaNotFoundError("Таймаут при проверке Java")
    except Exception as e:
        raise JavaNotFoundError(f"Ошибка при поиске Java: {e}")


def _get_jre_fonts_dir(java_home: Path) -> Path:
    """Получает путь к директории шрифтов JRE.

    Args:
        java_home: Путь к корню Java установки.

    Returns:
        Path: Путь к lib/fonts или lib/fonts/fallback.

    Raises:
        FontInitializationError: Если директория не найдена.
    """
    # Возможные пути (зависит от версии Java и ОС)
    possible_paths = [
        java_home / "lib" / "fonts",
        java_home / "jre" / "lib" / "fonts",
        java_home / "lib" / "fonts" / "fallback",
        java_home / "jre" / "lib" / "fonts" / "fallback",
    ]

    for fonts_path in possible_paths:
        if fonts_path.exists():
            logger.debug(f"📁 Найдена директория шрифтов JRE: {fonts_path}")
            return fonts_path

    # Если не нашли, создаем lib/fonts
    default_path = java_home / "lib" / "fonts"
    try:
        default_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Создана директория шрифтов: {default_path}")
        return default_path
    except Exception as e:
        raise FontInitializationError(
            f"Не удалось создать директорию шрифтов: {e}\n"
            f"Возможно требуются права администратора."
        )


def _copy_fonts_to_jre(jre_fonts_dir: Path) -> list[str]:
    """Копирует TTF шрифты в директорию JRE.

    Args:
        jre_fonts_dir: Путь к директории шрифтов JRE.

    Returns:
        list[str]: Список скопированных шрифтов.

    Raises:
        FontInitializationError: Если копирование не удалось.
    """
    if not FONTS_DIR.exists():
        raise FontInitializationError(f"Директория с шрифтами не найдена: {FONTS_DIR}")

    copied_fonts = []

    for font_file in FONTS_DIR.glob("*.ttf"):
        try:
            destination = jre_fonts_dir / font_file.name

            # Пропускаем если уже существует
            if destination.exists():
                logger.debug(f"⏭️  Шрифт уже установлен: {font_file.name}")
                copied_fonts.append(font_file.name)
                continue

            shutil.copy2(font_file, destination)
            logger.info(f"💉 Шрифт скопирован: {font_file.name}")
            copied_fonts.append(font_file.name)

        except PermissionError:
            raise FontInitializationError(
                f"Отказано в доступе при копировании {font_file.name}.\n"
                f"Требуются права администратора для установки шрифтов в JRE."
            )
        except Exception as e:
            logger.error(f"❌ Ошибка копирования {font_file.name}: {e}")

    if not copied_fonts:
        raise FontInitializationError("Не удалось скопировать ни одного шрифта")

    return copied_fonts


def _create_marker_file(java_home: Path, fonts: list[str]) -> None:
    """Создает маркер-файл об успешной установке шрифтов.

    Args:
        java_home: Путь к Java установке.
        fonts: Список установленных шрифтов.
    """
    marker_data = {
        "java_home": str(java_home),
        "fonts_installed": fonts,
        "platform": platform.system(),
        "timestamp": str(Path(__file__).stat().st_mtime),
    }

    try:
        with open(MARKER_FILE, "w", encoding="utf-8") as f:
            json.dump(marker_data, f, indent=2)
        logger.debug(f"✅ Создан маркер-файл: {MARKER_FILE}")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось создать маркер-файл: {e}")


def _check_marker_file() -> dict | None:
    """Проверяет наличие маркер-файла установки шрифтов.

    Returns:
        dict | None: Данные из маркера или None если файл отсутствует/невалиден.
    """
    if not MARKER_FILE.exists():
        return None

    try:
        with open(MARKER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Проверяем актуальность (Java существует)
        java_home = Path(data.get("java_home", ""))
        if java_home.exists():
            logger.debug(f"✅ Найден маркер установки шрифтов: {MARKER_FILE}")
            return data
        else:
            logger.debug(f"⚠️ Java из маркера не найдена, требуется переустановка")
            return None

    except Exception as e:
        logger.warning(f"⚠️ Ошибка чтения маркер-файла: {e}")
        return None


def ensure_fonts_initialized() -> dict:
    """Гарантирует, что кастомные шрифты установлены в JRE.

    Проверяет маркер-файл и если шрифты еще не установлены,
    выполняет установку автоматически.

    Returns:
        dict: Результат инициализации со структурой:
            {
                "success": bool,
                "already_installed": bool,
                "java_home": str,
                "fonts": list[str],
                "error": str | None
            }

    Raises:
        JavaNotFoundError: Если Java не найдена.
        FontInitializationError: Если установка не удалась.
    """
    logger.info("🔧 Проверка инициализации шрифтов...")

    # Проверяем маркер
    marker_data = _check_marker_file()
    if marker_data:
        logger.info(f"✅ Шрифты уже установлены в JRE: {marker_data['java_home']}")
        return {
            "success": True,
            "already_installed": True,
            "java_home": marker_data["java_home"],
            "fonts": marker_data["fonts_installed"],
            "error": None,
        }

    # Установка требуется
    logger.info("🚀 Начало установки шрифтов в JRE...")

    try:
        # 1. Находим Java
        java_home = _find_java_home()

        # 2. Получаем директорию шрифтов
        jre_fonts_dir = _get_jre_fonts_dir(java_home)

        # 3. Копируем шрифты
        installed_fonts = _copy_fonts_to_jre(jre_fonts_dir)

        # 4. Создаем маркер
        _create_marker_file(java_home, installed_fonts)

        logger.info(
            f"🎉 Шрифты успешно установлены! Скопировано: {len(installed_fonts)}"
        )

        return {
            "success": True,
            "already_installed": False,
            "java_home": str(java_home),
            "fonts": installed_fonts,
            "error": None,
        }

    except JavaNotFoundError as e:
        error_msg = (
            f"❌ Java не найдена в системе.\n\n"
            f"Пожалуйста, установите Java Runtime Environment (JRE) версии 8 или выше:\n"
            f"  • Windows: https://adoptium.net/\n"
            f"  • macOS: brew install openjdk\n"
            f"  • Linux: sudo apt-get install default-jre\n\n"
            f"Детали: {e}"
        )
        logger.error(error_msg)
        return {
            "success": False,
            "already_installed": False,
            "java_home": None,
            "fonts": [],
            "error": error_msg,
        }

    except FontInitializationError as e:
        error_msg = f"❌ Ошибка установки шрифтов: {e}"
        logger.error(error_msg)
        return {
            "success": False,
            "already_installed": False,
            "java_home": None,
            "fonts": [],
            "error": error_msg,
        }
