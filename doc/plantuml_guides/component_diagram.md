# Component Diagram Guide

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
component "Name" <<Stereotype>>
[ShortName] <<Stereotype>>
```

**Доступные стереотипы (ОБЯЗАТЕЛЬНО использовать для архитектурных диаграмм):**

- `<<Adapter>>` — Входные точки: API, UI, Views, Controllers. Цвет: Зелёный/Белый.
- `<<Core>>` — Бизнес-логика: Services, UseCases, Domain. Цвет: Жёлтый/Золотой.
- `<<Infrastructure>>` — Инфраструктура: БД, Кеш, Внешние API. Цвет: Синий/Серый.

**Связи:**

- `A --> B` — зависимость
- `A ..> B` — пунктирная зависимость
- `A --( B` — интерфейс

**Группировка:**

```plantuml
package "Layer Name" {
    component "A"
    component "B"
}
```
<!-- BRIEF_END -->

<!-- DETAILED_START -->
## Примеры использования

### Трёхслойная архитектура

```plantuml
@startuml
package "Presentation Layer" {
    component "Web API" <<Adapter>>
    component "CLI" <<Adapter>>
}

package "Business Layer" {
    component "Order Service" <<Core>>
    component "Payment Service" <<Core>>
    component "Notification Service" <<Core>>
}

package "Data Layer" {
    component "PostgreSQL" <<Infrastructure>>
    component "Redis Cache" <<Infrastructure>>
    component "Email Gateway" <<Infrastructure>>
}

[Web API] --> [Order Service]
[CLI] --> [Order Service]
[Order Service] --> [Payment Service]
[Order Service] --> [Notification Service]
[Order Service] --> [PostgreSQL]
[Order Service] --> [Redis Cache]
[Notification Service] --> [Email Gateway]
@enduml
```

### Hexagonal Architecture

```plantuml
@startuml
package "Adapters (Input)" {
    component "REST API" <<Adapter>>
    component "GraphQL" <<Adapter>>
    component "CLI" <<Adapter>>
}

package "Core (Domain)" {
    component "User Service" <<Core>>
    component "Order Service" <<Core>>
    component "Domain Events" <<Core>>
}

package "Adapters (Output)" {
    component "PostgreSQL Adapter" <<Infrastructure>>
    component "Redis Adapter" <<Infrastructure>>
    component "Kafka Producer" <<Infrastructure>>
}

[REST API] --> [User Service]
[GraphQL] --> [User Service]
[CLI] --> [Order Service]

[User Service] --> [PostgreSQL Adapter]
[Order Service] --> [Redis Adapter]
[Domain Events] --> [Kafka Producer]
@enduml
```

### Интерфейсы

```plantuml
@startuml
interface "IUserRepository" as IUR
interface "ICacheService" as ICS

component "User Service" <<Core>> as US
component "PostgreSQL Repository" <<Infrastructure>> as PG
component "Redis Cache" <<Infrastructure>> as RC

US --> IUR
US --> ICS
PG ..|> IUR
RC ..|> ICS
@enduml
```

## Частые ошибки

1. **Забыли стереотип:**
   - ❌ `component "Service"` — не понятна роль
   - ✅ `component "Service" <<Core>>` — бизнес-логика

2. **Неправильный синтаксис стереотипа:**
   - ❌ `component "API" <Adapter>`
   - ✅ `component "API" <<Adapter>>`

3. **Смешивание слоёв:**
   - Adapter не должен напрямую обращаться к Infrastructure
   - Только через Core!

## Рекомендации по слоям

### Adapter Layer (Зелёный/Белый)

- REST Controllers

* GraphQL Resolvers
- CLI Commands
- Web Views
- Message Consumers

### Core Layer (Жёлтый/Золотой)

- Domain Services

* Use Cases
- Domain Entities
- Business Rules
- Domain Events

### Infrastructure Layer (Синий/Серый)

- Database Repositories

* Cache Clients
- External API Clients
- Message Producers
- File Storage

## Styling & Themes

⚠️ **КРИТИЧЕСКИ ВАЖНО ДЛЯ AI МОДЕЛЕЙ:**

**ЗАПРЕЩЕНО:**
- ❌ Использовать `!theme` или `!include` директивы
- ❌ Жёстко прописывать цвета (например: `#backgroundColor red`)
- ❌ Переопределять стили через `skinparam` в diagram_code

**ПРАВИЛЬНЫЙ ПОДХОД:**
- ✅ Используйте ТОЛЬКО стереотипы: `<<Adapter>>`, `<<Core>>`, `<<Infrastructure>>`
- ✅ ВСЕГДА вызывайте `list_plantuml_themes` перед генерацией диаграммы
- ✅ Передавайте выбранную тему через параметр `theme_name`
- ✅ Доверьте цвета и стили теме — ваша задача структура, а не внешний вид

**Пример правильного использования:**

```plantuml
@startuml
component "API Gateway" <<Adapter>>
component "User Service" <<Core>>
component "PostgreSQL" <<Infrastructure>>
@enduml
```

## Production-Ready Example

**Это полноценный пример из реальных тестов проекта (`tests/assets/component_diagram.puml`).**

Демонстрирует правильную многослойную архитектуру с разделением входных адаптеров, бизнес-логики и инфраструктуры:

```plantuml
@startuml
' Тестовая диаграмма компонентов для интеграционного теста

package "Presentation Layer" {
  component "Django Views" <<Adapter>> as Views
  component "REST API" <<Adapter>> as API
  component "GraphQL API" <<Adapter>> as GraphQL
}

package "Business Logic Layer" {
  component "Order Service" <<Core>> as OrderSvc
  component "Payment Logic" <<Core>> as PaymentLogic
  component "Inventory Service" <<Core>> as InventorySvc
  component "Notification Service" <<Core>> as NotifySvc
}

package "Data Access Layer" {
  component "PostgreSQL Client" <<Infrastructure>> as PgSQL
  component "Redis Cache" <<Infrastructure>> as Redis
  component "S3 Storage" <<Infrastructure>> as S3
  component "Email Gateway" <<Infrastructure>> as Email
}

Views --> OrderSvc
API --> OrderSvc
GraphQL --> OrderSvc

OrderSvc --> PaymentLogic
OrderSvc --> InventorySvc
OrderSvc --> NotifySvc

PaymentLogic --> PgSQL
InventorySvc --> PgSQL
InventorySvc --> Redis
NotifySvc --> Email
OrderSvc --> S3

note right of OrderSvc
  Центральный сервис
  координирует бизнес-процессы
end note

@enduml
```

**Ключевые моменты:**

- ✅ Используются ТОЛЬКО стереотипы (<<Adapter>>, <<Core>>, <<Infrastructure>>)
- ✅ НЕТ директив !theme, !include, skinparam
- ✅ НЕТ жёстко прописанных цветов (#RRGGBB)
- ✅ Чистый PlantUML код, готовый к использованию с любой темой
- ✅ Правильное разделение по слоям: Presentation → Business Logic → Data Access
- ✅ Использование псевдонимов (as) для компактности

<!-- DETAILED_END -->
