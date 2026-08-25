# Task Manager API

REST API для управления пользователями и задачами. Сервис поддерживает регистрацию
и авторизацию по JWT, создание и редактирование задач, назначение исполнителя и
контроль доступа при удалении задач.

## Технологии

- Python 3.11+
- FastAPI
- SQLAlchemy 2 (asyncio)
- PostgreSQL
- Alembic
- Pydantic
- Pytest
- Docker Compose
- uv

## Возможности

- регистрация и авторизация пользователей;
- JWT-аутентификация;
- просмотр пользователей;
- создание, просмотр, обновление и удаление задач;
- миграции базы данных;
- интеграционные тесты API.

## Быстрый запуск через Docker Compose

Создайте файл `.env` на основе примера .env.example

Запустите приложение и PostgreSQL:

```bash
docker compose up --build
```

После запуска доступны:

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- проверка состояния: <http://localhost:8000/health>

При старте контейнера API команда `alembic upgrade head` выполняется автоматически.

Чтобы также удалить локальный том с данными PostgreSQL:

```bash
docker compose down -v
```

## Переменные окружения

Пример конфигурации находится в `.env.example`.

Для тестов дополнительно задайте URL отдельной тестовой базы:

```dotenv
TEST_DATABASE_URL=postgresql://task_manager:task_manager_password@localhost:5433/task_manager_test
```

Не используйте рабочую базу в `TEST_DATABASE_URL`: тестовая фикстура удаляет все
таблицы после завершения тестовой сессии.

## Локальный запуск

Установите [uv](https://docs.astral.sh/uv/), запустите PostgreSQL и установите
зависимости:

```bash
uv sync
docker compose up -d db
```

Укажите локальный URL базы и примените миграции:

```bash
DATABASE_URL="postgresql://task_manager:task_manager_password@localhost:5433/task_manager" \
uv run alembic upgrade head
```

Запустите сервер разработки:

```bash
DATABASE_URL="postgresql://task_manager:task_manager_password@localhost:5433/task_manager" \
uv run uvicorn main:app --reload
```

## Тесты

Тестовая база должна существовать до запуска тестов. Её URL задаётся переменной
`TEST_DATABASE_URL`.

Запуск тестов:

```bash
uv run pytest
```

## API

Все маршруты, кроме регистрации, входа и `/health`, требуют заголовок:

```text
Authorization: Bearer <access_token>
```

### Пользователи

| Метод | Маршрут | Описание |
| --- | --- | --- |
| `POST` | `/users/register/` | Регистрация пользователя |
| `POST` | `/users/login/` | Получение JWT-токена |
| `GET` | `/users/` | Список пользователей |
| `GET` | `/users/{user_id}/` | Пользователь по идентификатору |

### Задачи

| Метод | Маршрут | Описание |
| --- | --- | --- |
| `POST` | `/tasks/` | Создать задачу |
| `GET` | `/tasks/` | Получить список задач |
| `GET` | `/tasks/{task_id}` | Получить задачу |
| `PATCH` | `/tasks/{task_id}` | Обновить задачу |
| `DELETE` | `/tasks/{task_id}` | Удалить задачу |

Пример регистрации:

```bash
curl -X POST http://localhost:8000/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret"}'
```

Пример входа:

```bash
curl -X POST http://localhost:8000/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret"}'
```

Пример создания задачи:

```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"title":"Подготовить отчёт","description":"Собрать результаты за неделю"}'
```

## Структура проекта

```text
app/
├── api/           # маршруты и Pydantic-схемы
├── core/          # конфигурация, безопасность и исключения
├── db/            # подключение к БД и SQLAlchemy-модели
├── repositories/  # слой доступа к данным
├── services/      # бизнес-логика
└── utils/         # Unit of Work
alembic/           # конфигурация и версии миграций
docker/            # сценарий запуска контейнера
tests/             # интеграционные тесты API
main.py            # точка входа FastAPI
```
