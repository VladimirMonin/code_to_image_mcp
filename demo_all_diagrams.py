"""Демонстрация всех типов диаграмм в обеих темах."""

from diagram_renderer import render_diagram_from_string

# 1. ДИАГРАММА КОМПОНЕНТОВ (Component Diagram)
component_diagram = """
@startuml
!include asset/themes/{theme}.puml

package "Web Layer" {
    component "Django Views" <<Adapter>>
    component "REST API" <<Adapter>>
}

package "Business Layer" {
    component "Order Service" <<Core>>
    component "Payment Logic" <<Core>>
    component "Validation" <<Core>>
}

package "Data Layer" {
    component "PostgreSQL" <<Infrastructure>>
    component "Redis Cache" <<Infrastructure>>
    component "S3 Storage" <<Infrastructure>>
}

"Django Views" --> "Order Service"
"REST API" --> "Order Service"
"Order Service" --> "Payment Logic"
"Order Service" --> "Validation"
"Payment Logic" --> "PostgreSQL"
"Validation" --> "Redis Cache"
"Order Service" --> "S3 Storage"

note right of "Order Service"
  Ключевая бизнес-логика
  со стереотипом <<Core>>
end note
@enduml
"""

# 2. ДИАГРАММА ПОСЛЕДОВАТЕЛЬНОСТИ (Sequence Diagram)
sequence_diagram = """
@startuml
!include asset/themes/{theme}.puml

actor User
participant "REST API" as API
participant "Order Service" as OrderSvc
participant "Payment Logic" as PaymentSvc
participant "PostgreSQL" as DB

User -> API: POST /orders
activate API

API -> OrderSvc: create_order(data)
activate OrderSvc

OrderSvc -> OrderSvc: validate_data()
OrderSvc -> PaymentSvc: process_payment(amount)
activate PaymentSvc

PaymentSvc -> DB: save_transaction()
activate DB
DB --> PaymentSvc: transaction_id
deactivate DB

PaymentSvc --> OrderSvc: payment_confirmed
deactivate PaymentSvc

OrderSvc -> DB: save_order()
activate DB
DB --> OrderSvc: order_id
deactivate DB

OrderSvc --> API: order_created
deactivate OrderSvc

API --> User: 201 Created
deactivate API
@enduml
"""

# 3. ДИАГРАММА АКТИВНОСТИ (Activity Diagram)
activity_diagram = """
@startuml
!include asset/themes/{theme}.puml

start
:Получить запрос на заказ;

if (Данные валидны?) then (да)
  :Создать заказ <<Core>>;
  
  fork
    :Обработать оплату <<Core>>;
  fork again
    :Отправить email;
  fork again
    :Обновить кеш <<Infrastructure>>;
  end fork
  
  if (Оплата успешна?) then (да)
    :Сохранить в БД <<Infrastructure>>;
    :Вернуть order_id;
    stop
  else (нет)
    :Откатить транзакцию;
    :Вернуть ошибку;
    stop
  endif
  
else (нет)
  :Вернуть ошибку валидации;
  stop
endif
@enduml
"""

# 4. ДИАГРАММА КЛАССОВ (Class Diagram)
class_diagram = """
@startuml
!include asset/themes/{theme}.puml

class "OrderController" <<Adapter>> {
  +create_order(request)
  +get_order(order_id)
  +list_orders()
}

class "OrderService" <<Core>> {
  -validator: Validator
  -payment: PaymentService
  +create_order(data)
  +validate_order(data)
  +calculate_total(items)
}

class "PaymentService" <<Core>> {
  -gateway: PaymentGateway
  +process_payment(amount)
  +refund_payment(transaction_id)
}

class "OrderRepository" <<Infrastructure>> {
  -db_connection: Connection
  +save(order)
  +find_by_id(id)
  +find_all()
}

class "PaymentGateway" <<Infrastructure>> {
  -api_key: str
  +charge(amount)
  +verify_transaction(id)
}

"OrderController" --> "OrderService"
"OrderService" --> "PaymentService"
"OrderService" --> "OrderRepository"
"PaymentService" --> "PaymentGateway"
@enduml
"""


def render_all_diagrams(theme_name: str, scale: float = 2.5):
    """Генерирует все типы диаграмм для указанной темы."""

    diagrams = {
        "component": ("Компонентов", component_diagram),
        "sequence": ("Последовательности", sequence_diagram),
        "activity": ("Активности", activity_diagram),
        "class": ("Классов", class_diagram),
    }

    emoji = "🌑" if theme_name == "dark_gold" else "🌿"
    theme_display = "Dark Gold" if theme_name == "dark_gold" else "Light Fresh"

    print(f"\n{emoji} === {theme_display} ===")

    for diagram_type, (name, diagram_code) in diagrams.items():
        diagram_with_theme = diagram_code.replace("{theme}", theme_name)
        output_path = f"tests/output/{diagram_type}_{theme_name}.png"

        render_diagram_from_string(
            diagram_with_theme,
            output_path,
            format="png",
            theme_name=theme_name,
            scale_factor=scale,
        )

        print(f"  ✅ Диаграмма {name}: {output_path}")


# Генерируем все диаграммы для обеих тем
print("🎨 Генерируем полную демонстрацию всех типов диаграмм...")
print("=" * 70)

render_all_diagrams("dark_gold", scale=2.5)
render_all_diagrams("light_fresh", scale=2.5)

print("\n" + "=" * 70)
print("✅ Готово! Создано 8 диаграмм (4 типа × 2 темы):")
print("\n📊 Типы диаграмм:")
print("  1. Component (Компонентов) - архитектура системы")
print("  2. Sequence (Последовательности) - взаимодействие объектов")
print("  3. Activity (Активности) - бизнес-процессы")
print("  4. Class (Классов) - структура классов")
print("\n🎨 Темы:")
print("  🌑 Dark Gold - строгая темная с золотым акцентом")
print("  🌿 Light Fresh - мягкая светлая мятная")
print("\n📁 Все файлы в: tests/output/")
