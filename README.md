Простой блог, в котором можно публиковать статьи и видеть реакцию пользователей в виде комментариев.

#### Основные функции
- Просмотр постов: все пользователи, включая неавторизованных, могут просматривать список постов, а также выполняться фильтрацию по тэгам
- Регистрация: пользователи могут регистрироваться в системе используя email и пароль
- Авторизация: пользователи могут авторизоваться в системе. После авторизации доступны дополнительные функции
- Создание, редактирование и удаление постов: любой авторизованный пользователь может создавать посты, а также редактировать или удалять свои посты
- Комментирование: авторизованные пользователи могут оставлять комментарии к постам и отвечать на другие комментарии. При ответе на комментарии образуются ветки комментариев

#### Стек технологий
- Фронтенд:
  - HTML, CSS, JavaScript
  - Bootstrap для стилизации и адаптивного дизайна
  - Fetch API для взаимодействия с бэкендом

- Бэкенд:
  - Python
  - FastAPI
  - Pydantic
  - Alembic для миграций
  - JWT-токены для аутентификации

- База данных
  - PostgreSQL

- Инфраструктура:
  - Docker, Docker Compose
  - GitHub (для хранения кода и CI/CD)

#### Установка и запуск

- Предварительные требования
  - Установите Docker и Docker Compose
  - Убедитесь, что порты 8000 (бэкенд) и 80 (фронтенд) свободны

- Инструкции по запуску
  - Клонируйте репозиторий:
    - git clone https://github.com/mmikhail-git/blog-engine.git
  - Запустите проект с помощью Docker Compose:
    - docker-compose up --build

 Демо проекта доступно по ссылке - http://forb1.tech/index.html 
