# Система аутентификации и авторизации

## Описание проекта
Backend-приложение с собственной системой разграничения прав доступа.

## Технологии
- Django 4.2 + DRF
- PostgreSQL
- Сессионная аутентификация

## Установка и запуск
1. Клонировать репозиторий
2. Создать виртуальное окружение
3. `pip install -r requirements.txt`
4. Настроить PostgreSQL (создать БД, пользователя)
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib libpq-dev
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    sudo systemctl status postgresql
    sudo -u postgres psql
        CREATE DATABASE user_management_db;
        CREATE USER myuser WITH PASSWORD 'mypassword';
        ALTER ROLE myuser SET client_encoding TO 'utf8';
        ALTER ROLE myuser SET default_transaction_isolation TO 'read committed';
        ALTER ROLE myuser SET timezone TO 'UTC';
        GRANT ALL PRIVILEGES ON DATABASE user_management_db TO myuser;
5. Настроить джанго на Postgress:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'user_management_db',
            'USER': 'myuser',
            'PASSWORD': 'mypassword',
            'HOST': 'localhost',       # или IP сервера, если удалённо
            'PORT': '5432',
        }
    }
5. `python manage.py migrate`
6. `python manage.py runserver`

## Схема БД (описание системы прав)

### Таблицы
- `Role` — роли пользователей (admin, user, manager)
- `BusinessElement` — объекты доступа (products, orders, users)
- `AccessRoleRule` — правила доступа (can_read_own, can_create, can_update_all и т.д.)

### Логика проверки прав
- При запросе определяется бизнес-элемент (например, `products`)
- Для роли пользователя находятся правила доступа
- Проверяются флаги в зависимости от HTTP-метода
- Для прав `*_own` проверяется `owner_id` объекта

## API эндпоинты

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | /api/users/register/ | Регистрация |
| POST | /api/users/login/ | Вход (сессия) |
| GET | /api/users/profile/ | Профиль |
| PATCH | /api/users/profile/ | Обновление профиля |
| POST | /api/users/logout/ | Выход |
| DELETE | /api/users/delete/ | Удаление аккаунта (мягкое) |
| GET | /api/users/mock/products/ | Список товаров (mock) |
| POST | /api/users/mock/products/ | Создать товар |
| DELETE | /api/users/mock/products/{id}/ | Удалить товар |
| GET | /api/users/admin/rules/ | Список правил (админ) |
| POST | /api/users/admin/rules/ | Создать правило |
| PUT | /api/users/admin/rules/{id}/ | Изменить правило |
| DELETE | /api/users/admin/rules/{id}/ | Удалить правило |

## Тестирование через curl

1. Регистрация пользователя:
    curl -X POST http://127.0.0.1:8000/api/users/register/ \
    -H "Content-Type: application/json" \
    -d '{
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "johnpass123",
        "password2": "johnpass123"
    }'

    Ожидаемый ответ (201 Created):
        {
        "id": 1,
        "email": "john@example.com",
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": true
        }

Далее для полноценного тестирования нужно создать роль:

python manage.py shell

from users.models import MyUser, Role

role, created = Role.objects.get_or_create(name='user')
print(f'Роль {"создана" if created else "уже существует"}')

user = MyUser.objects.get(email='john@example.com')

user.role = role
user.save()
print(f'Пользователю {user.email} назначена роль {user.role.name}')

2. Логин (с сохранением cookie):
    curl -X POST http://127.0.0.1:8000/api/users/login/ \
    -H "Content-Type: application/json" \
    -d '{"email": "john@example.com", "password": "johnpass123"}' \
    -c cookies.txt
    
    Ожидаемый ответ (200 OK):
        {
        "id": 1,
        "email": "john@example.com",
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": true
        }

3. Получить профиль:
    curl -X GET http://127.0.0.1:8000/api/users/profile/ -b cookies.txt

4. Обновить профиль (PATCH):
    curl -X PATCH http://127.0.0.1:8000/api/users/profile/ \
    -H "Content-Type: application/json" \
    -d '{"first_name": "Jonathan", "last_name": "Smith"}' \
    -b cookies.txt

5. Создать товар (требует права can_create):
    curl -X POST http://127.0.0.1:8000/api/users/mock/products/ \
    -H "Content-Type: application/json" \
    -d '{"name": "Мой первый товар"}' \
    -b cookies.txt
    
    Ожидаемый ответ (201 Created):
        {
        "message": "Товар создан",
        "product": {
            "id": 3,
            "name": "Мой первый товар",
            "owner_id": 1
        }
        }

6. Получить список товаров:
    curl -X GET http://127.0.0.1:8000/api/users/mock/products/ -b cookies.txt

7. Удалить товар (требует can_delete_own):
    curl -X DELETE http://127.0.0.1:8000/api/users/mock/products/3/ -b cookies.txt

8. Выход из системы:
    curl -X POST http://127.0.0.1:8000/api/users/logout/ -b cookies.txt

9. Мягкое удаление аккаунта:
    curl -X DELETE http://127.0.0.1:8000/api/users/delete/ -b cookies.txt

Для проверки админских эндпойнтов:
Создать админа и назначь роль:
python manage.py createsuperuser
python manage.py shell

    from users.models import MyUser, Role
    admin = MyUser.objects.get(email='admin@example.com')
    admin_role, _ = Role.objects.get_or_create(name='admin')
    admin.role = admin_role
    admin.save()

Залогиниться админом и сохранить cookie:
curl -X POST http://127.0.0.1:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "adminpass"}' \
  -c admin_cookies.txt

10. Список всех правил доступа:
    curl -X GET http://127.0.0.1:8000/api/users/admin/rules/ -b admin_cookies.txt

11. Создать новое правило (роль и элемент по id или можно использовать SlugRelatedField в сериализаторе):
    curl -X POST http://127.0.0.1:8000/api/users/admin/rules/ \
    -H "Content-Type: application/json" \
    -d '{
        "role": 1,
        "element": 1,
        "can_read_own": true,
        "can_create": true
    }' \
    -b admin_cookies.txt

12. Обновить правило:
    curl -X PUT http://127.0.0.1:8000/api/users/admin/rules/1/ \
    -H "Content-Type: application/json" \
    -d '{
        "role": 1,
        "element": 1,
        "can_read_all": true,
        "can_create": true,
        "can_update_all": true
    }' \
    -b admin_cookies.txt

13. Удалить правило:
    curl -X DELETE http://127.0.0.1:8000/api/users/admin/rules/2/ -b admin_cookies.txt


## Автор
Александр Клоповский