Локальное разворачивание проекта:

- Установите зависимости из requirements.txt
- Установите переменные в .env, примеры расположены в .env_sample
- Примините миграции
- Запустите Daphne-сервер:  daphne -p 8000 config.asgi:application
- Перейти по адресу:  http://localhost:8000/api/emails/
