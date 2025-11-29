"""Демонстрация работы логирования в font_initializer."""

import logging
import sys
from pathlib import Path

# Настройка логирования для демонстрации
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)

# Добавляем корень проекта
sys.path.insert(0, str(Path(__file__).parent.parent))

from font_initializer import ensure_fonts_initialized
from diagram_renderer import render_diagram_from_string


def main():
    """Демонстрация логирования."""
    print("\n" + "=" * 80)
    print("ДЕМОНСТРАЦИЯ ЛОГИРОВАНИЯ ИНИЦИАЛИЗАЦИИ ШРИФТОВ")
    print("=" * 80 + "\n")

    # 1. Инициализация шрифтов
    print("1. Вызов ensure_fonts_initialized():")
    print("-" * 80)
    result = ensure_fonts_initialized()
    print(
        f"\nРезультат: success={result['success']}, "
        f"already_installed={result['already_installed']}, "
        f"fonts={len(result['fonts'])}"
    )

    # 2. Рендеринг диаграммы
    print("\n" + "=" * 80)
    print("2. Рендеринг тестовой диаграммы:")
    print("-" * 80)

    diagram_code = """@startuml
skinparam defaultFontName "JetBrains Mono"
Alice -> Bob: Hello with JetBrains Mono!
@enduml"""

    output_path = Path(__file__).parent / "output" / "demo_logging.png"
    render_result = render_diagram_from_string(
        diagram_code=diagram_code,
        output_path=str(output_path),
        format="png",
        theme_name=None,
    )

    print(f"\nРезультат рендеринга: {output_path}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
