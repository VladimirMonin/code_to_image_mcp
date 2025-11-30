# Руководство по созданию PlantUML темы для code_to_image_mcp

## Введение

Этот документ описывает как создать полностью совместимую PlantUML тему для проекта `code_to_image_mcp`, чтобы избежать проблем с читаемостью элементов (черный текст на темном фоне, невидимые обводки и т.д.).

## Критические элементы PlantUML

PlantUML имеет **множество специфичных элементов**, которые **игнорируют** глобальные настройки (`defaultFontColor`, `backgroundColor`) и требуют **явного переопределения**.

### Обязательный чеклист элементов

При создании темы необходимо явно прописать настройки для **ВСЕХ** следующих элементов:

#### 1. Заголовок и легенда

```plantuml
' Title (заголовок диаграммы)
skinparam titleFontColor #ЦВЕТ_ТЕКСТА
skinparam titleFontSize 18
skinparam titleBorderColor #ЦВЕТ_ОБВОДКИ
skinparam titleBorderThickness 2
skinparam titleBackgroundColor #ЦВЕТ_ФОНА

' Legend (легенда/описание)
skinparam legendFontColor #ЦВЕТ_ТЕКСТА
skinparam legendBackgroundColor #ЦВЕТ_ФОНА
skinparam legendBorderColor #ЦВЕТ_ОБВОДКИ
skinparam legendBorderThickness 2
```

**Частая проблема:** Черная обводка легенды на темном фоне — выглядит как двойная рамка.

#### 2. Заметки (Notes)

```plantuml
skinparam note {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}
```

#### 3. Специфичные участники Sequence диаграмм

```plantuml
' Database (база данных)
skinparam database {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}

' Collections (коллекции)
skinparam collections {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}

' Queue (очередь)
skinparam queue {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}

' Entity (сущность)
skinparam entity {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}

' Boundary (граница системы)
skinparam boundary {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}

' Control (контроллер)
skinparam control {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}

' Actor (актор)
skinparam actor {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}
```

**Частая проблема:** Database/Queue/Entity получают черные обводки на темном фоне.

#### 4. Activity диаграммы

```plantuml
' Основные элементы activity
skinparam activity {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
    DiamondBackgroundColor #ЦВЕТ_РОМБА
    DiamondBorderColor #ЦВЕТ_ОБВОДКИ_РОМБА
    DiamondFontColor #ЦВЕТ_ТЕКСТА_РОМБА
    StartColor #ЦВЕТ_СТАРТА
    EndColor #ЦВЕТ_ФИНИША
    BarColor #ЦВЕТ_ПОЛОС
}

' Кружки начала/завершения (ОБЯЗАТЕЛЬНО!)
skinparam activityStart {
    Color #ЦВЕТ_СТАРТА
}

skinparam activityEnd {
    Color #ЦВЕТ_ФИНИША
}

' CRITICAL! PlantUML игнорирует activityEnd для stop элементов
' Используйте глобальные параметры:
skinparam ActivityEndColor #ЦВЕТ_ФИНИША
skinparam ActivityStopColor #ЦВЕТ_ФИНИША

' Partition (блоки валидация/обработка)
skinparam partition {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}

' Swimlane (дорожки ответственности)
skinparam swimlane {
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    TitleFontColor #ЦВЕТ_ТЕКСТА
}
```

**Частые проблемы:**

- Черный кружок `stop` на темном фоне
- Черная обводка `partition` — выглядит как сплошной черный блок

#### 5. Deployment элементы

```plantuml
' Node (узел)
skinparam node {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}

' Cloud (облако)
skinparam cloud {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}

' Folder (папка)
skinparam folder {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}

' Artifact (артефакт)
skinparam artifact {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}
```

#### 6. Другие элементы

```plantuml
' Frame (фрейм в sequence)
skinparam frame {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}

' State (состояния)
skinparam state {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}

' Package (пакеты)
skinparam package {
    BackgroundColor #ЦВЕТ_ФОНА
    BorderColor #ЦВЕТ_ОБВОДКИ
    BorderThickness 2
    FontColor #ЦВЕТ_ТЕКСТА
}
```

## Рекомендации по цветам

### Для темных тем (темный фон)

- **Обводки:** яркие цвета (#569CD6, #4EC9B0, #007ACC)
- **Текст:** светлый (#D4D4D4, #FFFFFF, #E8E8E8)
- **Фон элементов:** чуть светлее основного фона (#2D2D30 на #1E1E1E)
- **НИКОГДА не используйте:** черные обводки (#000000) или темно-серые (#222222)

### Для светлых тем (светлый фон)

- **Обводки:** насыщенные темные цвета (#294f3d, #2E7D32)
- **Текст:** темный (#0b2e1d, #1a1a1a, #000000)
- **Фон элементов:** чуть темнее основного фона (#F0FFF0 на #FFFFFF)

## Процесс создания темы

### 1. Создайте базовый файл

```plantuml
' === THEME: YOUR_THEME_NAME ===
' Описание темы

' 1. ГЛОБАЛЬНЫЕ НАСТРОЙКИ
skinparam backgroundColor #ВАШ_ОСНОВНОЙ_ФОН
skinparam defaultFontName "JetBrains Mono"
skinparam defaultFontSize 14
skinparam defaultFontColor #ВАШ_ОСНОВНОЙ_ЦВЕТ_ТЕКСТА
skinparam roundCorner 8
skinparam shadowing false

' 2. БАЗОВЫЕ ЭЛЕМЕНТЫ (class, component, usecase)
' ... ваши настройки ...

' 3. SEQUENCE ДИАГРАММЫ
skinparam sequence {
    ArrowColor #ЦВЕТ_СТРЕЛОК
    ParticipantBackgroundColor #ЦВЕТ_ФОНА
    ParticipantBorderColor #ЦВЕТ_ОБВОДКИ
    ParticipantFontColor #ЦВЕТ_ТЕКСТА
}

' 4. СТЕРЕОТИПЫ (ОБЯЗАТЕЛЬНО!)
skinparam class<<Adapter>> {
    BackgroundColor #ЦВЕТ_АДАПТЕРА
    BorderColor #ЦВЕТ_ОБВОДКИ_АДАПТЕРА
    FontColor #ЦВЕТ_ТЕКСТА
}

skinparam class<<Core>> {
    BackgroundColor #ЦВЕТ_ЯДРА
    BorderColor #ЦВЕТ_ОБВОДКИ_ЯДРА
    FontColor #ЦВЕТ_ТЕКСТА
}

skinparam class<<Infrastructure>> {
    BackgroundColor #ЦВЕТ_ИНФРАСТРУКТУРЫ
    BorderColor #ЦВЕТ_ОБВОДКИ_ИНФРАСТРУКТУРЫ
    FontColor #ЦВЕТ_ТЕКСТА
}

' Дублируем для component
skinparam component<<Adapter>> { ... }
skinparam component<<Core>> { ... }
skinparam component<<Infrastructure>> { ... }
```

### 2. Добавьте UNIVERSAL ELEMENT OVERRIDES

Скопируйте весь блок "UNIVERSAL ELEMENT OVERRIDES" из `default.puml` или `dark_gold.puml` и адаптируйте цвета под вашу палитру.

### 3. Протестируйте тему

Запустите визуальные тесты:

```bash
pytest tests/test_theme_visual_check.py -k "your_theme_name" -v
```

Проверьте следующие диаграммы:

- ✅ Component diagram — legend, notes, database, queue
- ✅ Sequence diagram — все типы участников (actor, database, entity, boundary, control)
- ✅ Class diagram — legend, notes, стереотипы
- ✅ Activity diagram — partition, swimlane, start/stop кружки

### 4. Проверьте контрастность

Откройте сгенерированные PNG файлы в `tests/output/theme_visual_check/` и убедитесь:

- ❌ НЕТ черного текста на темном фоне
- ❌ НЕТ черных обводок на темном фоне
- ✅ Все элементы читаемы
- ✅ Legend не имеет двойной обводки
- ✅ Partition блоки видны
- ✅ Start/stop кружки видны

## Типичные ошибки

### ❌ Ошибка 1: Забыли настроить legend

**Симптом:** Черная двойная обводка легенды на темном фоне.  
**Решение:** Добавьте `skinparam legend { BorderColor #СВЕТЛЫЙ_ЦВЕТ }`

### ❌ Ошибка 2: Забыли activityEnd

**Симптом:** Черный кружок `stop` на темном фоне.  
**Решение:** Добавьте `skinparam activityEnd { Color #ЦВЕТ }`

### ❌ Ошибка 3: Забыли partition

**Симптом:** Черная обводка блоков "Валидация", "Обработка" в activity.  
**Решение:** Добавьте `skinparam partition { BorderColor #СВЕТЛЫЙ_ЦВЕТ }`

### ❌ Ошибка 4: Забыли database/queue/entity

**Симптом:** Черные обводки специфичных участников sequence.  
**Решение:** Добавьте настройки для каждого типа участника.

## Примеры существующих тем

### 1. `default.puml` — темная VS Code тема

- Фон: `#1E1E1E`
- Текст: `#D4D4D4`
- Акценты: синий `#007ACC`, голубой `#569CD6`, зеленый `#4EC9B0`

### 2. `dark_gold.puml` — темная золотая тема

- Фон: `#1a1a1a`
- Текст: `#e0e0e0`
- Акценты: золотой `#d4af37`, серый `#888888`

### 3. `light_fresh.puml` — светлая мятная тема

- Фон: `#f0faf5`
- Текст: `#0b2e1d`
- Акценты: зеленый `#4dd191`, желтый `#e3c764`, синий `#b5beeb`

## Чеклист перед релизом темы

- [ ] Все 3 стереотипа (Adapter/Core/Infrastructure) настроены для class
- [ ] Все 3 стереотипа настроены для component
- [ ] Title имеет явный цвет текста и обводки
- [ ] Legend имеет явный цвет текста и обводки
- [ ] Note имеет настройки
- [ ] Database, Queue, Collections, Entity, Boundary, Control настроены
- [ ] Actor настроен
- [ ] Activity имеет настройки
- [ ] ActivityStart и ActivityEnd настроены ЯВНО
- [ ] Partition настроен
- [ ] Swimlane настроен
- [ ] Package настроен
- [ ] Node, Cloud, Folder, Artifact настроены
- [ ] Запущены визуальные тесты
- [ ] Все диаграммы проверены на читаемость

## Где разместить тему

Сохраните файл в `asset/themes/your_theme_name.puml`.

Тема автоматически станет доступна через:

- MCP инструмент `list_plantuml_themes`
- Параметр `theme_name` в `generate_architecture_diagram`

## Дополнительная информация

Если возникают вопросы по PlantUML элементам, используйте:

- Официальная документация: <https://plantuml.com/>
- Тесты проекта: `tests/test_theme_visual_check.py`
- Существующие темы: `asset/themes/`
