# Sequence Diagram Guide

<!-- BRIEF_START -->
## ⚠️ КРИТИЧЕСКИ ВАЖНО ДЛЯ AI МОДЕЛЕЙ

**ЗАПРЕЩЕНО ИСПОЛЬЗОВАТЬ:**

- ❌ `!theme` или `!include` директивы
- ❌ `skinparam` настройки
- ❌ Жёстко прописанные цвета (#RRGGBB)

**ПРАВИЛЬНЫЙ ПОДХОД:**

- ✅ НЕ используйте стилизацию в sequence диаграммах
- ✅ Передавайте тему через параметр `theme_name`
- ✅ Генерируйте ЧИСТЫЙ PlantUML код без стилизации!

---

**Синтаксис участников:**

```plantuml
participant "Имя" as alias
actor "Актор" as actorAlias
database "БД" as db
```

**Синтаксис сообщений:**

- `A -> B: Сообщение` — синхронный запрос
- `A --> B: Ответ` — пунктирный ответ
- `A ->> B: Async` — асинхронный запрос
- `A -x B: Отмена` — отмена/ошибка

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
   - Если используете `activate`, не забудьте `deactivate`
   - Иначе бар активации уходит до конца диаграммы

2. **Неправильный порядок стрелок:**
   - `->` сплошная стрелка (запрос)
   - `-->` пунктирная стрелка (ответ)

3. **Кириллица без кавычек:**
   - ❌ `participant Пользователь`
   - ✅ `participant "Пользователь" as User`

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
- ❌ Использовать `!theme` или `!include` директивы
- ❌ Жёстко прописывать цвета (например: `skinparam sequenceMessageAlign center`)
- ❌ Переопределять стили через `skinparam` в diagram_code

**ПРАВИЛЬНЫЙ ПОДХОД:**
- ✅ ВСЕГДА вызывайте `list_plantuml_themes` перед генерацией диаграммы
- ✅ Передавайте выбранную тему через параметр `theme_name`
- ✅ Доверьте цвета и стили теме — ваша задача структура взаимодействий
- ✅ Используйте типизированных участников (`actor`, `database`, `participant`) для автоматической стилизации

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

## Production-Ready Example

**Это полноценный пример из реальных тестов проекта (`tests/assets/sequence_diagram.puml`).**

Демонстрирует полноценный сценарий создания заказа с активацией участников и взаимодействием между слоями:

```plantuml
@startuml
' Тестовая диаграмма последовательности для интеграционного теста

actor User as U
participant "Web App" as WA
participant "Order Service" as OS
participant "Payment Service" as PS
database "PostgreSQL" as DB

U -> WA: Создать заказ
activate WA

WA -> OS: create_order(user_id, items)
activate OS

OS -> OS: validate_items()
OS -> PS: calculate_total(items)
activate PS
PS --> OS: total_amount
deactivate PS

OS -> PS: process_payment(amount, card)
activate PS
PS -> DB: save_transaction()
activate DB
DB --> PS: transaction_id
deactivate DB
PS --> OS: payment_confirmed
deactivate PS

OS -> DB: save_order(order_data)
activate DB
DB --> OS: order_id
deactivate DB

OS --> WA: order_created
deactivate OS

WA --> U: Заказ №12345
deactivate WA

@enduml
```

**Ключевые моменты:**

- ✅ НЕТ директив !theme, !include, skinparam
- ✅ НЕТ жёстко прописанных цветов
- ✅ Правильное использование activate/deactivate для визуализации времени жизни
- ✅ Типизированные участники (actor, participant, database)
- ✅ Сплошные стрелки для запросов (->), пунктирные для ответов (-->)
- ✅ Чистый PlantUML код, готовый к использованию с любой темой

<!-- DETAILED_END -->
