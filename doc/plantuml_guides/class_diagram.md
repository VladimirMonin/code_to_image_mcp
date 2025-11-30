# Class Diagram Guide

<!-- BRIEF_START -->
## ⚠️ КРИТИЧЕСКИ ВАЖНО ДЛЯ AI МОДЕЛЕЙ

**ЗАПРЕЩЕНО ИСПОЛЬЗОВАТЬ:**

- ❌ `!theme` или `!include` директивы
- ❌ `skinparam` настройки
- ❌ Жёстко прописанные цвета (#RRGGBB)

**ПРАВИЛЬНЫЙ ПОДХОД:**

- ✅ Используйте ТОЛЬКО стереотипы: `<<Adapter>>`, `<<Core>>`, `<<Infrastructure>>`
- ✅ Передавайте тему через параметр `theme_name`
- ✅ Генерируйте ЧИСТЫЙ PlantUML код без стилизации!

---

**Синтаксис:**

```plantuml
class "ClassName" <<Stereotype>> {
    + publicField: Type
    - privateField: Type
    # protectedField: Type
    + publicMethod(): ReturnType
    - privateMethod(): ReturnType
}
```

**Доступные стереотипы (рекомендуется использовать):**

- `<<Adapter>>` — Входные точки: API, UI, Controllers, Views. Цвет: Зелёный/Белый.
- `<<Core>>` — Бизнес-логика: Services, UseCases, Domain. Цвет: Жёлтый/Золотой.
- `<<Infrastructure>>` — Инфраструктура: БД, Кеш, Внешние API, Repositories. Цвет: Синий/Серый.

**Отношения:**

- `A --|> B` — наследование (A extends B)
- `A ..|> B` — реализация интерфейса (A implements B)
- `A --> B` — ассоциация/зависимость
- `A --o B` — агрегация (A содержит B, но B может существовать отдельно)
- `A --* B` — композиция (A владеет B, B не может существовать без A)
<!-- BRIEF_END -->

<!-- DETAILED_START -->
## Примеры использования

### Простой класс

```plantuml
@startuml
class User {
    + id: int
    + name: String
    + email: String
    + register(): void
    + login(): bool
}
@enduml
```

### Класс со стереотипом

```plantuml
@startuml
class "UserService" <<Core>> {
    - repository: UserRepository
    + createUser(dto: CreateUserDTO): User
    + findById(id: int): User
}

class "UserController" <<Adapter>> {
    - service: UserService
    + handleCreate(request: Request): Response
}

class "UserRepository" <<Infrastructure>> {
    - connection: Connection
    + save(user: User): void
    + findById(id: int): User
}

UserController --> UserService
UserService --> UserRepository
@enduml
```

### Интерфейсы и наследование

```plantuml
@startuml
interface IRepository<T> {
    + findById(id: int): T
    + save(entity: T): void
    + delete(id: int): void
}

class "UserRepository" <<Infrastructure>> {
    + findById(id: int): User
    + save(entity: User): void
    + delete(id: int): void
}

UserRepository ..|> IRepository
@enduml
```

## Частые ошибки

1. **Забытые кавычки в именах с пробелами:**
   - ❌ `class User Service`
   - ✅ `class "User Service"`

2. **Неправильный синтаксис стереотипа:**
   - ❌ `class UserService <Core>`
   - ✅ `class "UserService" <<Core>>`

3. **Забытые модификаторы доступа:**
   - ❌ `name: String`
   - ✅ `+ name: String` (public)

## Модификаторы доступа

| Символ | Значение |
|--------|----------|
| `+` | public |
| `-` | private |
| `#` | protected |
| `~` | package |

## Styling & Themes

⚠️ **КРИТИЧЕСКИ ВАЖНО ДЛЯ AI МОДЕЛЕЙ:**

**ЗАПРЕЩЕНО:**
- ❌ Использовать `!theme` или `!include` директивы
- ❌ Жёстко прописывать цвета (например: `#backgroundColor yellow`)
- ❌ Переопределять стили через `skinparam` в diagram_code

**ПРАВИЛЬНЫЙ ПОДХОД:**
- ✅ Используйте ТОЛЬКО стереотипы: `<<Adapter>>`, `<<Core>>`, `<<Infrastructure>>`
- ✅ ВСЕГДА вызывайте `list_plantuml_themes` перед генерацией диаграммы
- ✅ Передавайте выбранную тему через параметр `theme_name`
- ✅ Доверьте цвета и стили теме — ваша задача структура классов и их отношения

**Пример правильного использования:**

```plantuml
@startuml
class "UserController" <<Adapter>> {
    + createUser(dto: CreateUserDTO): Response
}

class "UserService" <<Core>> {
    + registerUser(dto: CreateUserDTO): User
}

class "UserRepository" <<Infrastructure>> {
    + save(user: User): void
}

UserController --> UserService
UserService --> UserRepository
@enduml
```

## Production-Ready Example

**Это полноценный пример из реальных тестов проекта (`tests/assets/class_diagram.puml`).**

Демонстрирует правильное использование стереотипов для 3-слойной архитектуры заказов:

```plantuml
@startuml
' Тестовая диаграмма классов для интеграционного теста

class "OrderController" <<Adapter>> {
  - order_service: OrderService
  + create_order(request: Request): Response
  + get_order(order_id: int): Response
  + list_orders(): Response
}

class "OrderService" <<Core>> {
  - repository: OrderRepository
  - payment: PaymentService
  + create_order(data: dict): Order
  + validate_order(data: dict): bool
  + calculate_total(items: list): float
}

class "PaymentService" <<Core>> {
  - gateway: PaymentGateway
  - validator: PaymentValidator
  + process_payment(amount: float): bool
  + refund_payment(transaction_id: str): bool
}

class "OrderRepository" <<Infrastructure>> {
  - db_connection: Connection
  + save(order: Order): int
  + find_by_id(id: int): Order
  + find_all(): list
}

class "PaymentGateway" <<Infrastructure>> {
  - api_key: str
  - endpoint: str
  + charge(amount: float, token: str): str
  + verify(transaction_id: str): bool
}

"OrderController" --> "OrderService" : uses
"OrderService" --> "PaymentService" : uses
"OrderService" --> "OrderRepository" : uses
"PaymentService" --> "PaymentGateway" : uses

@enduml
```

**Ключевые моменты:**

- ✅ Используются ТОЛЬКО стереотипы (<<Adapter>>, <<Core>>, <<Infrastructure>>)
- ✅ НЕТ директив !theme, !include, skinparam
- ✅ НЕТ жёстко прописанных цветов (#RRGGBB)
- ✅ Чистый PlantUML код, готовый к использованию с любой темой
- ✅ Правильное разделение ответственности по слоям

<!-- DETAILED_END -->
