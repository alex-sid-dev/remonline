# Код-ревью проекта Remonline

Дата: 19.02.2026

---

## Статус реализации плана

| # | Задача | Статус |
|---|--------|--------|
| 1 | Пагинация во все `read_all_*` эндпоинты | ✅ Выполнено |
| 2 | Миграция с индексами БД | ✅ Выполнено |
| 3 | Debounce на поля поиска | ✅ Выполнено |
| 4 | Вынести дублирующиеся утилиты | ✅ Выполнено |
| 5 | Исправить типизацию `Optional[]` | ✅ Выполнено |
| 6 | Бизнес-логика из handlers в сервисы | ✅ Выполнено |
| 7 | Inline-стили → CSS-классы | ✅ Выполнено |
| 8 | Декомпозиция App.vue (модалки) | ✅ Выполнено |
| 9 | Composables (useRolePermissions) | ✅ Выполнено |
| 10 | Исправить мутацию пропсов | ✅ Выполнено |
| 11 | Тесты command handlers | ✅ Выполнено |
| 12 | Тесты пермишенов | ✅ Выполнено |
| 13 | CORS-конфигурация | ✅ Выполнено |
| 14 | Rate limiting | ✅ Выполнено |

---

## Что было сделано

### Фаза 1: Производительность

#### 1.1 Пагинация
- Все порты (`ClientReader`, `OrderReader`, `EmployeeReader`, `PartReader`) теперь принимают `limit`/`offset` и возвращают `Tuple[List[...], int]`
- Адаптеры выполняют `COUNT(*)` + `LIMIT/OFFSET` SQL-запросы
- Command handlers оборачивают результат в `PaginatedResponse` (items, total, limit, offset)
- API-эндпоинты принимают `limit` и `offset` как Query-параметры
- Фронтенд обновлён для обработки нового формата ответа

#### 1.2 Индексы БД
- Создана миграция `add_performance_indexes` с 8 индексами:
  - `orders.status`, `orders.is_active`, `orders.(is_active, created_at)`
  - `employees.is_active`, `clients.is_active`
  - `order_comments.order_id`, `order_parts.order_id`, `works.employee_id`
- Индексы добавлены в ORM-определения таблиц

#### 1.3 Debounce
- Создан утилит `frontend/src/utils/debounce.js`
- Debounce (300ms) применён к поиску клиентов в `OrderList.vue`
- Debounce применён к поиску запчастей в `PartsList.vue`

### Фаза 2: Качество кода

#### 2.4 Утилиты
- `frontend/src/constants/roles.js` — константы ролей + permission-хелперы
- `frontend/src/utils/inputHelpers.js` — `blockNonNumeric`, `isValidPhone`
- `frontend/src/utils/errorHelpers.js` — `extractErrorMessage`
- Все компоненты обновлены для использования этих утилит

#### 2.5 Типизация
- `EmployeeService.update_employee()` — параметры `phone`, `full_name`, `position` теперь `Optional[...]`

#### 2.6 Бизнес-логика
- `OrderService.assign_engineer_to_unassigned_works()` — вынесено из `UpdateOrderCommandHandler`
- Исправлен формат `EntityNotFoundError` — все используют `message=`

#### 2.7 CSS-классы
- Создано 10 CSS-утилит: `.mt-16`, `.border-top-subtle`, `.text-right`, `.cursor-pointer`, `.btn-danger`, `.form-title`, `.inline-form-cell` и др.
- Inline-стили заменены во всех компонентах

### Фаза 3: Архитектура фронтенда

#### 3.8 Декомпозиция App.vue
Из App.vue выделено 5 модальных компонентов:
- `ClientModal.vue` — создание клиента
- `DeviceModal.vue` — создание устройства
- `PartModal.vue` — создание/редактирование запчасти
- `WorkModal.vue` — добавление работы
- `OrderPartModal.vue` — привязка запчасти к заказу

App.vue уменьшен с ~1307 до ~380 строк (шаблон + скрипт).

#### 3.9 Composables
- `useRolePermissions.js` — computed-обёртки для permission-функций

#### 3.10 Мутация пропсов
- `OrderDetail.vue` — все `props.orderDetails.data = updated` заменены на `emit('update:order', updated)`
- Родитель (`App.vue`) обрабатывает `@update:order` и обновляет состояние

### Фаза 4: Надёжность

#### 4.11-12 Тесты
Создан `tests/test_command_handlers.py` — 32 теста:
- Пагинация ReadAll-хендлеров (9 тестов)
- UpdateOrderCommandHandler (6 тестов)
- Пермишены UpdateEmployeeCommandHandler (9 тестов)
- ChangePasswordCommandHandler (8 тестов)

Общий итог: **73 теста, все пройдены**.

#### 4.13 CORS
- Добавлены `http://localhost:5173` и `http://127.0.0.1:5173` в `cors_origins`

#### 4.14 Rate Limiting
- Установлен `slowapi` (200 req/min per IP)
- Создан `src/config/rate_limit.py`
- Подключен в `create_app()` с обработчиком `RateLimitExceeded`

---

## Добавлен rollback в Transaction

- `Transaction` (порт) теперь имеет метод `rollback()`
- `TransactionAlchemy` реализует его через `session.rollback()`

---

## Структура после рефакторинга

```
frontend/src/
├── App.vue                      (~380 строк, было ~1307)
├── components/
│   ├── ClientModal.vue          NEW
│   ├── DeviceModal.vue          NEW
│   ├── EmployeeForm.vue         обновлён (утилиты, CSS, ROLES)
│   ├── EmployeeList.vue         обновлён (утилиты)
│   ├── LoginModal.vue
│   ├── OrderDetail.vue          обновлён (emit вместо мутации, утилиты)
│   ├── OrderList.vue            обновлён (debounce, утилиты)
│   ├── OrderPartModal.vue       NEW
│   ├── PartModal.vue            NEW
│   ├── PartsList.vue            обновлён (debounce, утилиты)
│   └── WorkModal.vue            NEW
├── composables/
│   ├── useAuth.js               обновлён (ROLES)
│   └── useRolePermissions.js    NEW
├── constants/
│   └── roles.js                 NEW
├── services/
│   └── api.js
├── utils/
│   ├── debounce.js              NEW
│   ├── errorHelpers.js          NEW
│   ├── inputHelpers.js          NEW
│   └── orderHelpers.js
└── style.css                    обновлён (+10 утилит)
```
