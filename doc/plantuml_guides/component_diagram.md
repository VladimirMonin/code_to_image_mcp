# Component Diagram Guide

<!-- BRIEF_START -->
**Синтаксис:**
```plantuml
component "Name" <<Stereotype>>
[ShortName] <<Stereotype>>
```

**Доступные стереотипы (ОБЯЗАТЕЛЬНО использовать для архитектурных диаграмм):**
* `<<Adapter>>` — Входные точки: API, UI, Views, Controllers. Цвет: Зелёный/Белый.
* `<<Core>>` — Бизнес-логика: Services, UseCases, Domain. Цвет: Жёлтый/Золотой.
* `<<Infrastructure>>` — Инфраструктура: БД, Кеш, Внешние API. Цвет: Синий/Серый.

**Связи:**
* `A --> B` — зависимость
* `A ..> B` — пунктирная зависимость
* `A --( B` — интерфейс

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
- GraphQL Resolvers
- CLI Commands
- Web Views
- Message Consumers

### Core Layer (Жёлтый/Золотой)
- Domain Services
- Use Cases
- Domain Entities
- Business Rules
- Domain Events

### Infrastructure Layer (Синий/Серый)
- Database Repositories
- Cache Clients
- External API Clients
- Message Producers
- File Storage
<!-- DETAILED_END -->
