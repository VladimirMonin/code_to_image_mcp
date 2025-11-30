# Class Diagram Guide

<!-- BRIEF_START -->
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
* `<<Adapter>>` — Входные точки: API, UI, Controllers, Views. Цвет: Зелёный/Белый.
* `<<Core>>` — Бизнес-логика: Services, UseCases, Domain. Цвет: Жёлтый/Золотой.
* `<<Infrastructure>>` — Инфраструктура: БД, Кеш, Внешние API, Repositories. Цвет: Синий/Серый.

**Отношения:**
* `A --|> B` — наследование (A extends B)
* `A ..|> B` — реализация интерфейса (A implements B)
* `A --> B` — ассоциация/зависимость
* `A --o B` — агрегация (A содержит B, но B может существовать отдельно)
* `A --* B` — композиция (A владеет B, B не может существовать без A)
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
<!-- DETAILED_END -->
