# Selection Committee

Приложение Django для приёмной комиссии: анкеты, личные кабинеты, документы, рейтинги и выгрузки.

## Установка и запуск

Требуется Python 3.11 или новее. Node.js и распаковка архивов не нужны.

С помощью uv:

```powershell
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Либо через Python и pip:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Откройте http://127.0.0.1:8000/. Административная панель: /admin/.
По умолчанию используется SQLite. Миграции создают таблицы и обновляют старые статусы; существующую базу удалять не нужно.
Если окружение ссылается на удалённый Python, сохраните его в `.venv.bak` и создайте новое.

## Работа

Абитуриент подаёт анкету на /form/. Сотрудник принимает её в административной панели; приложение создаёт учётную запись, документы, родителей и заявление. Пользователь может изменять только свою анкету.
Выгрузки и создание заявлений доступны сотрудникам. Обновление школ выполняется кнопкой в административной панели; при ошибке загрузки старый список сохраняется.

## Настройки

Переменные окружения перечислены в `.env.example`. Файл автоматически не загружается: установите переменные в оболочке или настройках сервера.
Локально письма выводятся в консоль. Для SMTP задайте `DJANGO_EMAIL_BACKEND`, `EMAIL_HOST_USER` и `EMAIL_HOST_PASSWORD`.
Для размещения на сервере задайте `DJANGO_DEBUG=0`, уникальный `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` и выполните:

```powershell
python manage.py collectstatic --noinput
```

Исходные ресурсы находятся в `static/`, собранные — в `staticfiles/`, пользовательские файлы — в `media/`.

## Проверки

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Тесты используют отдельную базу данных.
