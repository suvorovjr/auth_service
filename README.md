# **Auth Microservice**

Этот микросервис отвечает за **аутентификацию, авторизацию и управление ролями** пользователей. Он поддерживает авторизацию по email/паролю и через **OAuth (Яндекс)**, а также предоставляет механизмы управления правами доступа.  

## **Технологии**
- **Python 3.12**  
- **FastAPI** — веб-фреймворк  
- **SQLAlchemy** — ORM  
- **PostgreSQL** — база данных  
- **Redis** — хранение черного списка токенов  
- **Alembic** — миграции базы данных  
- **Docker & Docker Compose**  
- **Pytest** — тестирование  
- **Authlib** — интеграция с OAuth  
- **Uvicorn** — ASGI-сервер  

## **Структура проекта**
```plaintext
├── alembic/                     # Миграции базы данных
├── nginx/                        # Конфигурация NGINX
├── src/                          # Исходный код приложения
│   ├── api/v1/                   # API эндпоинты
│   │   ├── schemas/              # Pydantic-схемы запросов и ответов
│   │   ├── auth.py               # Эндпоинты аутентификации
│   │   ├── me.py                 # Эндпоинты для профиля пользователя
│   │   ├── oauth.py              # OAuth-авторизация
│   │   ├── permission.py         # Управление правами доступа
│   │   ├── roles.py              # Управление ролями
│   ├── core/                     # Основные настройки и обработка исключений
│   │   ├── config.py             # Конфигурация сервиса
│   │   ├── exception_handlers.py # Обработчики ошибок
│   │   ├── logger.py             # Логирование
│   ├── db/                       # Подключение к БД и Redis
│   ├── domain/                   # Бизнес-логика (сущности, интерфейсы, репозитории)
│   ├── infrastructure/           # Реализация репозиториев
│   ├── services/                 # Сервисы (Auth, OAuth, Session и т. д.)
│   ├── tests/                    # Тесты (юнит и функциональные)
├── .env.example                  # Пример конфигурационного файла
├── docker-compose.yml             # Конфигурация Docker
├── Dockerfile                     # Образ для микросервиса
├── Makefile                        # Команды для быстрого запуска
├── requirements.txt                # Зависимости проекта
└── README.md                       # Документация (этот файл)
```

## **Установка и запуск**
### **1. Настройка окружения**
```bash
cp .env.example .env
```
Заполни `.env` своими настройками.

### **2. Запуск в Docker**
```bash
docker-compose up --build
```

### **3. Запуск локально**
```bash
python -m venv .venv
source .venv/bin/activate  # Для Linux/Mac
.venv\Scripts\activate     # Для Windows
pip install -r requirements.txt
alembic upgrade head       # Применение миграций
uvicorn src.main:app --reload
```

---

## **API эндпоинты**
### **1. Аутентификация (`/api/v1/auth`)**
| Метод  | Эндпоинт          | Описание |
|--------|------------------|----------|
| `POST` | `/register/`     | Регистрация пользователя |
| `POST` | `/login/`        | Логин пользователя |
| `POST` | `/logout/`       | Выход из системы |
| `POST` | `/refresh/`      | Обновление токена |
| `POST` | `/logout-others/`| Выход из всех сессий кроме текущей |

---

### **2. Профиль (`/api/v1/me`)**
| Метод  | Эндпоинт                     | Описание |
|--------|-----------------------------|----------|
| `GET`  | `/`                         | Получить данные профиля |
| `GET`  | `/{uuid}/sessions/`         | Получить активные сессии |
| `POST` | `/change-password/`         | Изменение пароля |

---

### **3. OAuth (Яндекс) (`/api/v1/oauth`)**
| Метод  | Эндпоинт               | Описание |
|--------|-----------------------|----------|
| `GET`  | `/yandex/login`       | Получить URL для авторизации |
| `GET`  | `/yandex/callback`    | Callback после авторизации |

---

### **4. Управление правами (`/api/v1/permissions`)**
| Метод  | Эндпоинт            | Описание |
|--------|--------------------|----------|
| `GET`  | `/`                | Получить список прав |
| `GET`  | `/{slug}/`         | Получить конкретное право |
| `POST` | `/`                | Создать новое право |
| `PATCH`| `/{slug}/`         | Изменить право |
| `DELETE` | `/{slug}/`       | Удалить право |

---

### **5. Управление ролями (`/api/v1/roles`)**
| Метод  | Эндпоинт                  | Описание |
|--------|--------------------------|----------|
| `GET`  | `/`                      | Получить список ролей |
| `GET`  | `/{slug}/`               | Получить конкретную роль |
| `POST` | `/`                      | Создать новую роль |
| `PATCH`| `/{slug}/`               | Изменить роль |
| `DELETE` | `/{slug}/`             | Удалить роль |
| `POST` | `/add-role-to-user/`     | Добавить роль пользователю |
| `POST` | `/delete-role-from-user/` | Удалить роль у пользователя |

---

## **Тестирование**
```bash
pytest
```
Тесты хранятся в `tests/unit/`.

## 👨‍💻 **Автор**

[Павел Главан / GitHub профиль]

✉️ Email: pglavan1998@gmail.com

🚀 GitHub: https://github.com/suvorovjr
