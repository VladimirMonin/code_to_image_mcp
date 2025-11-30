# Sequence Diagram Guide

<!-- BRIEF_START -->
**Синтаксис участников:**

```plantuml
participant "Имя" as alias
actor "Актор" as actorAlias
database "БД" as db
```

**Синтаксис сообщений:**

* `A -> B: Сообщение` — синхронный запрос
* `A --> B: Ответ` — пунктирный ответ
* `A ->> B: Async` — асинхронный запрос
* `A -x B: Отмена` — отмена/ошибка

**Активация (lifeline bars):**

```plantuml
activate A
A -> B: Запрос
deactivate A
```

**Группировка:**

```plantuml
alt условие
    A -> B: если true
else иначе
    A -> B: если false
end
```
<!-- BRIEF_END -->

<!-- DETAILED_START -->
## Примеры использования

### Простая последовательность

```plantuml
@startuml
Alice -> Bob: Привет!
Bob --> Alice: Привет, как дела?
Alice -> Bob: Отлично, спасибо!
@enduml
```

### Участники с типами

```plantuml
@startuml
actor "Пользователь" as User
participant "API Gateway" as API
participant "Auth Service" as Auth
database "База данных" as DB

User -> API: POST /login
activate API
API -> Auth: validateCredentials()
activate Auth
Auth -> DB: SELECT user
activate DB
DB --> Auth: userData
deactivate DB
Auth --> API: token
deactivate Auth
API --> User: 200 OK + JWT
deactivate API
@enduml
```

### Условия и циклы

```plantuml
@startuml
participant Client
participant Server

alt успешная авторизация
    Client -> Server: login(valid_credentials)
    Server --> Client: 200 OK
else неверный пароль
    Client -> Server: login(invalid_credentials)
    Server --> Client: 401 Unauthorized
end

loop каждые 5 минут
    Client -> Server: heartbeat()
    Server --> Client: pong
end
@enduml
```

### Заметки

```plantuml
@startuml
Alice -> Bob: Сообщение
note left: Заметка слева
note right: Заметка справа
note over Alice, Bob: Заметка над обоими
@enduml
```

## Частые ошибки

1. **Забыли deactivate:**
   * Если используете `activate`, не забудьте `deactivate`
   * Иначе бар активации уходит до конца диаграммы

2. **Неправильный порядок стрелок:**
   * `->` сплошная стрелка (запрос)
   * `-->` пунктирная стрелка (ответ)

3. **Кириллица без кавычек:**
   * ❌ `participant Пользователь`
   * ✅ `participant "Пользователь" as User`

## Типы участников

| Тип | Описание |
|-----|----------|
| `participant` | Обычный участник (прямоугольник) |
| `actor` | Человек-актор (фигурка) |
| `database` | База данных (цилиндр) |
| `entity` | Сущность |
| `boundary` | Граница системы |
| `control` | Контроллер |
| `collections` | Коллекция |
| `queue` | Очередь |

## Styling & Themes

⚠️ **КРИТИЧЕСКИ ВАЖНО ДЛЯ AI МОДЕЛЕЙ:**

**ЗАПРЕЩЕНО:**
* ❌ Использовать `!theme` или `!include` директивы
* ❌ Жёстко прописывать цвета (например: `skinparam sequenceMessageAlign center`)
* ❌ Переопределять стили через `skinparam` в diagram_code

**ПРАВИЛЬНЫЙ ПОДХОД:**
* ✅ ВСЕГДА вызывайте `list_plantuml_themes` перед генерацией диаграммы
* ✅ Передавайте выбранную тему через параметр `theme_name`
* ✅ Доверьте цвета и стили теме — ваша задача структура взаимодействий
* ✅ Используйте типизированных участников (`actor`, `database`, `participant`) для автоматической стилизации

**Пример правильного использования:**

```plantuml
@startuml
actor User
participant "API Gateway" as API
database "PostgreSQL" as DB

User -> API: POST /login
API -> DB: SELECT user
DB --> API: user data
API --> User: JWT token
@enduml
```
<!-- DETAILED_END -->
