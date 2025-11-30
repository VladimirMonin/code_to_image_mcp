"""Визуальные тесты для проверки тем PlantUML на всех элементах."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.diagram_renderer import render_diagram_from_string


@pytest.fixture
def visual_output_dir():
    """Директория для визуальных артефактов."""
    output = Path(__file__).parent / "output" / "theme_visual_check"
    output.mkdir(parents=True, exist_ok=True)
    return output


class TestThemeVisualCheck:
    """Визуальные тесты для проверки цветов всех элементов на всех темах."""

    THEMES = ["default", "dark_gold", "light_fresh"]

    def _generate_component_diagram_full(self) -> str:
        """Компонентная диаграмма со ВСЕМИ элементами для проверки."""
        return """
@startuml
title Component Diagram - Full Elements Test
note as N1
  Эта диаграмма тестирует:
  * Title
  * Legend
  * Notes
  * Все стереотипы
  * Спецсимволы PlantUML
end note

package "Presentation Layer" {
  component "Django Views" <<Adapter>> as Views
  component "REST API" <<Adapter>> as API
}

package "Business Logic Layer" {
  component "Order Service" <<Core>> as OrderSvc
  component "Payment Logic" <<Core>> as PaymentLogic
}

package "Data Access Layer" {
  database "PostgreSQL" <<Infrastructure>> as PgSQL
  queue "RabbitMQ" <<Infrastructure>> as Queue
  collections "Redis Cache" <<Infrastructure>> as Redis
}

Views --> OrderSvc
API --> OrderSvc
OrderSvc --> PaymentLogic
PaymentLogic --> PgSQL
OrderSvc --> Queue
OrderSvc --> Redis

note right of OrderSvc
  Центральный сервис
  координирует процессы
end note

note left of PgSQL
  Основное хранилище
end note

legend right
  |= Стереотип |= Назначение |
  | <<Adapter>> | Входные точки |
  | <<Core>> | Бизнес-логика |
  | <<Infrastructure>> | Инфраструктура |
endlegend

@enduml
"""

    def _generate_sequence_diagram_full(self) -> str:
        """Sequence диаграмма со ВСЕМИ элементами."""
        return """
@startuml
title Sequence Diagram - Full Elements Test

actor User as U
participant "Web App" as WA
participant "Order Service" as OS
database "PostgreSQL" as DB
entity "Order" as Order
boundary "Payment Gateway" as PG
control "Validator" as Val

note over U, Val
  Проверка всех типов участников:
  actor, participant, database,
  entity, boundary, control
end note

U -> WA: Создать заказ
activate WA

WA -> Val: validate_input()
activate Val
Val --> WA: OK
deactivate Val

WA -> OS: create_order(data)
activate OS

OS -> DB: save_order()
activate DB
DB --> OS: order_id
deactivate DB

OS -> PG: charge(amount)
activate PG
PG --> OS: transaction_id
deactivate PG

OS --> WA: order_created
deactivate OS

WA --> U: Заказ №12345
deactivate WA

note right of U
  Пользователь получает
  подтверждение
end note

legend bottom
  Легенда проверяет читаемость
  текста на фоне темы
endlegend

@enduml
"""

    def _generate_class_diagram_full(self) -> str:
        """Class диаграмма со ВСЕМИ элементами."""
        return """
@startuml
title Class Diagram - Full Elements Test

class "OrderController" <<Adapter>> {
  - order_service: OrderService
  + create_order(request): Response
  + get_order(id): Response
}

class "OrderService" <<Core>> {
  - repository: OrderRepository
  + create_order(data): Order
  + validate_order(data): bool
}

class "OrderRepository" <<Infrastructure>> {
  - db: Connection
  + save(order): int
  + find_by_id(id): Order
}

note top of OrderController
  Входная точка API
  Обрабатывает HTTP запросы
end note

note bottom of OrderService
  Бизнес-логика заказов
end note

note left of OrderRepository
  Слой данных
  PostgreSQL
end note

"OrderController" --> "OrderService" : uses
"OrderService" --> "OrderRepository" : uses

legend right
  |= Цвет |= Слой |
  | Зелёный | Adapter |
  | Золотой | Core |
  | Синий | Infrastructure |
endlegend

@enduml
"""

    def _generate_activity_diagram_full(self) -> str:
        """Activity диаграмма со ВСЕМИ элементами."""
        return """
@startuml
title Activity Diagram - Full Elements Test

start

note right
  Тестируем:
  * Title
  * Notes
  * Partition
  * Fork/Join
end note

partition "Валидация" {
  :Проверить токен;
  
  if (Токен валиден?) then (да)
    :Извлечь user_id;
  else (нет)
    :Вернуть 401;
    stop
  endif
}

partition "Обработка" {
  fork
    :Валидировать товары;
  fork again
    :Проверить склад;
  fork again
    :Применить промокод;
  end fork
  
  :Создать заказ;
  
  if (Оплата?) then (да)
    :Обработать платёж;
    
    if (Успешно?) then (да)
      :Подтвердить;
      :Отправить email;
    else (нет)
      :Откатить;
      note right
        Ошибка оплаты
      end note
      stop
    endif
  else (нет)
    :Зарезервировать;
  endif
}

:Вернуть результат;
stop

legend bottom
  Легенда внизу диаграммы
  для проверки цвета текста
endlegend

@enduml
"""

    @pytest.mark.parametrize("theme", THEMES)
    def test_component_diagram_all_themes(self, visual_output_dir, theme):
        """Проверка component диаграммы на всех темах."""
        code = self._generate_component_diagram_full()
        output_file = visual_output_dir / f"component_{theme}.png"

        result = render_diagram_from_string(
            diagram_code=code,
            output_path=str(output_file),
            format="png",
            theme_name=theme,
            scale_factor=2.0,  # Medium для быстрой проверки
        )

        assert result["success"] is True
        assert output_file.exists()
        assert result["theme_used"] == theme

    @pytest.mark.parametrize("theme", THEMES)
    def test_sequence_diagram_all_themes(self, visual_output_dir, theme):
        """Проверка sequence диаграммы на всех темах."""
        code = self._generate_sequence_diagram_full()
        output_file = visual_output_dir / f"sequence_{theme}.png"

        result = render_diagram_from_string(
            diagram_code=code,
            output_path=str(output_file),
            format="png",
            theme_name=theme,
            scale_factor=2.0,
        )

        assert result["success"] is True
        assert output_file.exists()
        assert result["theme_used"] == theme

    @pytest.mark.parametrize("theme", THEMES)
    def test_class_diagram_all_themes(self, visual_output_dir, theme):
        """Проверка class диаграммы на всех темах."""
        code = self._generate_class_diagram_full()
        output_file = visual_output_dir / f"class_{theme}.png"

        result = render_diagram_from_string(
            diagram_code=code,
            output_path=str(output_file),
            format="png",
            theme_name=theme,
            scale_factor=2.0,
        )

        assert result["success"] is True
        assert output_file.exists()
        assert result["theme_used"] == theme

    @pytest.mark.parametrize("theme", THEMES)
    def test_activity_diagram_all_themes(self, visual_output_dir, theme):
        """Проверка activity диаграммы на всех темах."""
        code = self._generate_activity_diagram_full()
        output_file = visual_output_dir / f"activity_{theme}.png"

        result = render_diagram_from_string(
            diagram_code=code,
            output_path=str(output_file),
            format="png",
            theme_name=theme,
            scale_factor=2.0,
        )

        assert result["success"] is True
        assert output_file.exists()
        assert result["theme_used"] == theme

    def test_summary_report(self, visual_output_dir):
        """Генерация сводного отчёта по результатам визуальных тестов."""
        report_file = visual_output_dir / "VISUAL_CHECK_REPORT.md"

        report_content = """# Отчёт визуальной проверки тем PlantUML

## Цель проверки
Убедиться что все элементы PlantUML (title, legend, notes, database, queue, etc) 
имеют правильные цвета текста на всех темах.

## Проверяемые элементы
- ✅ Title (заголовок диаграммы)
- ✅ Legend (легенда)
- ✅ Notes (заметки/комментарии)
- ✅ Database (база данных)
- ✅ Queue (очередь)
- ✅ Collections (коллекции)
- ✅ Entity (сущность)
- ✅ Actor (актор)
- ✅ Boundary (граница)
- ✅ Control (контроллер)
- ✅ Partition (раздел в activity)
- ✅ Стереотипы (<<Adapter>>, <<Core>>, <<Infrastructure>>)

## Проверяемые темы
1. **default** — стандартная тема
2. **dark_gold** — тёмная тема с золотыми акцентами
3. **light_fresh** — светлая тема с зелёными акцентами

## Типы диаграмм
1. Component Diagram
2. Sequence Diagram
3. Class Diagram
4. Activity Diagram

## Инструкция по проверке
1. Откройте папку `tests/output/theme_visual_check/`
2. Просмотрите все PNG файлы
3. **Критерий прохождения**: весь текст должен быть читаемым, нет чёрного текста на тёмном фоне
4. Если найдены проблемы — запишите их ниже

---

## Результаты проверки

### default тема
- [ ] component_default.png - OK / ПРОБЛЕМЫ: ___
- [ ] sequence_default.png - OK / ПРОБЛЕМЫ: ___
- [ ] class_default.png - OK / ПРОБЛЕМЫ: ___
- [ ] activity_default.png - OK / ПРОБЛЕМЫ: ___

### dark_gold тема
- [ ] component_dark_gold.png - OK / ПРОБЛЕМЫ: ___
- [ ] sequence_dark_gold.png - OK / ПРОБЛЕМЫ: ___
- [ ] class_dark_gold.png - OK / ПРОБЛЕМЫ: ___
- [ ] activity_dark_gold.png - OK / ПРОБЛЕМЫ: ___

### light_fresh тема
- [ ] component_light_fresh.png - OK / ПРОБЛЕМЫ: ___
- [ ] sequence_light_fresh.png - OK / ПРОБЛЕМЫ: ___
- [ ] class_light_fresh.png - OK / ПРОБЛЕМЫ: ___
- [ ] activity_light_fresh.png - OK / ПРОБЛЕМЫ: ___

---

## Найденные проблемы
(Заполняется после визуальной проверки)

1. 
2. 
3. 

"""

        report_file.write_text(report_content, encoding="utf-8")
        assert report_file.exists()
