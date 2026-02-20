# RemOnline

Система управления сервисным центром: бэкенд на FastAPI, фронтенд на Vue 3. Заказы, клиенты, устройства, сотрудники, запчасти, работы, статистика, печать актов и квитанций.

## Стек

- **Backend**: Python 3.12, FastAPI, SQLAlchemy (async), Alembic, Dishka (DI), Keycloak (auth)
- **Frontend**: Vue 3, Vite, Axios
- **Database**: PostgreSQL 16
- **Auth**: Keycloak 26

## Архитектура бэкенда

Бэкенд построен по принципам **Clean Architecture**: домен в центре, зависимости направлены внутрь.

```
src/
├── entities/          # Доменный слой: сущности и сервисы (Order, Client, Employee, ...)
├── application/       # Command handlers, порты (интерфейсы), ошибки
├── infra/             # Адаптеры к БД/Keycloak, ORM-модели, миграции
├── presentation/      # REST API (FastAPI), схемы, валидаторы
└── config/            # Настройки, DI (Dishka), логирование, маппинг таблиц
```

Подробнее: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Запуск

### Через Docker Compose

```bash
docker compose up -d
```

Сервисы:
- API: http://localhost:8000/api/docs
- Frontend: http://localhost:5173
- Keycloak: http://localhost:8080

### Локальная разработка

1. Скопируйте `.env.example` в `.env` и заполните значения:
   ```bash
   cp .env.example .env
   ```

2. Запустите PostgreSQL и Keycloak (например, через Docker Compose без сервиса `app`).

3. Установите зависимости и запустите:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   alembic upgrade head
   uvicorn src.main:app --reload
   ```

4. Фронтенд:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Тесты

```bash
pip install -e ".[test]"
pytest
```

## Миграции

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Документация

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — архитектура бэкенда, слои, порты, роли.
- В интерфейсе раздел **«Справка»** — создание и редактирование заказов, права доступа, ограничения.
