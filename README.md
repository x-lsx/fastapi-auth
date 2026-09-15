# FastAPI Auth

Сервис аутентификации пользователей на FastAPI. Проект предоставляет регистрацию
и вход пользователей, JWT-токены, подтверждение email, смену пароля и получение
профиля авторизованного пользователя.

## О проекте

Приложение построено как асинхронный API-сервис. PostgreSQL используется для
хранения пользователей, Redis - для refresh- и verification-токенов, а Celery -
для фоновой отправки писем подтверждения email.

Интерактивная документация API доступна по адресу `/api/docs` после запуска
приложения. Стандартный адрес локального API: `http://localhost:8000`.

## Возможности

- регистрация пользователя с хешированием пароля;
- вход по email и паролю;
- выдача access- и refresh-токенов в формате JWT;
- обновление access-токена по refresh-токену;
- отзыв refresh-токена при выходе;
- подтверждение email по ссылке из письма;
- смена пароля авторизованным пользователем;
- получение профиля текущего пользователя;
- проверка состояния сервиса через healthcheck endpoint;
- автоматическое обновление и отзыв токенов через Redis;
- отправка писем подтверждения в Celery-задаче;
- CORS с настройкой разрешённых источников через переменные окружения.

## Технологический стек

- **Python 3.12**
- **FastAPI** и **Uvicorn** - HTTP API и ASGI-сервер
- **Pydantic Settings** - конфигурация приложения
- **SQLAlchemy 2.0** и **asyncpg** - асинхронная работа с PostgreSQL
- **Alembic** - миграции базы данных
- **Redis** - хранение токенов и брокер фоновых задач
- **Celery** - фоновые задачи
- **JWT**, `PyJWT`, `bcrypt`, `passlib` - аутентификация и хеширование паролей
- **aiosmtplib** - отправка email
- **Docker Compose** - запуск API, PostgreSQL, Redis и Celery worker

## Структура проекта

```text
.
├── app/
│   ├── core/              # Конфигурация, JWT, безопасность, зависимости, Celery
│   ├── db/                # Подключения и lifecycle PostgreSQL/Redis
│   ├── models/            # SQLAlchemy-модели
│   ├── repositories/      # Работа с данными
│   ├── routes/            # HTTP-роуты FastAPI
│   ├── schemas/           # Pydantic-схемы запросов и ответов
│   ├── services/          # Бизнес-логика авторизации, токенов и пользователей
│   ├── tasks/              # Celery-задачи
│   └── main.py            # Создание FastAPI-приложения
├── migrations/            # Конфигурация Alembic и шаблон миграций
├── .env.example           # Пример переменных окружения
├── alembic.ini            # Конфигурация Alembic
├── docker-compose.yaml    # Сервисы API, PostgreSQL, Redis и worker
├── dockerfile             # Образ приложения
└── requirements.txt       # Python-зависимости
```

## Запуск

### Запуск через Docker Compose

1. Создайте файл `.env` на основе `.env.example`.
2. Заполните обязательные параметры PostgreSQL, Redis, JWT и SMTP.
3. Укажите также `CELERY_BROKER_URL` и `CELERY_RESULT_URL` - они используются
   конфигурацией Celery.
4. Запустите сервисы:

   ```bash
   docker compose up --build
   ```

После запуска:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/api/docs`
- Healthcheck: `http://localhost:8000/health`

### Локальный запуск

Установите зависимости и подготовьте `.env.local`:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Для локального запуска отдельно должны быть доступны PostgreSQL и Redis, а
также настроены SMTP-параметры и переменные окружения из конфигурации
приложения.

## API

Все endpoints доступны без дополнительного префикса. Для защищённых endpoints
используется заголовок:

```text
Authorization: Bearer <access_token>
```

| Метод | Endpoint | Авторизация | Назначение |
| --- | --- | --- | --- |
| `GET` | `/` | Нет | Информация о сервисе |
| `GET` | `/health` | Нет | Проверка доступности API |
| `POST` | `/auth/register` | Нет | Регистрация пользователя и выдача токенов |
| `POST` | `/auth/login` | Нет | Вход и выдача токенов |
| `POST` | `/auth/refresh` | Нет | Обновление пары токенов по refresh-токену |
| `POST` | `/auth/logout` | Нет | Отзыв refresh-токена |
| `GET` | `/auth/verify?token=...` | Нет | Подтверждение email |
| `PATCH` | `/auth/change-password` | Bearer | Смена пароля текущего пользователя |
| `GET` | `/user/profile` | Bearer | Получение профиля текущего пользователя |

### Пример регистрации

```http
POST /auth/register
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "secret123"
}
```

Ответ содержит `access_token`, `refresh_token`, тип токена и время жизни обоих
токенов в секундах.

### Пример смены пароля

```http
PATCH /auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "secret123",
  "new_password": "new-secret123"
}
```

## Что надо доделать

- добавить полноценную миграцию Alembic для таблицы `users` и проверить
  миграционный процесс на чистой базе;
- реализовать восстановление пароля: endpoints для запроса письма, проверки
  токена и установки нового пароля;
- добавить обновление профиля пользователя через API
  (`UserService.update_user` уже содержит соответствующую бизнес-логику);
- добавить тесты для регистрации, входа, refresh/logout, подтверждения email,
  смены пароля и проверки прав доступа;
- добавить отдельные настройки и документацию для production-окружения
  (секреты, HTTPS, CORS, SMTP и ротация JWT-ключей);
- вынести диагностическую Celery-задачу для login из production-кода или
  заменить её на полноценное логирование;
- синхронизировать `.env.example` со всеми обязательными настройками,
  включая переменные Celery;
- проверить переносимость Docker-сборки на Linux: имя файла в
  `docker-compose.yaml` должно совпадать с регистром имени Dockerfile.
