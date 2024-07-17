# Бэкенд. Работа с конференциями

Управление конференциями

## Установка

1. Клонируйте репозиторий на свой локальный компьютер.
2. Установите все необходимые зависимости, выполнив `pip install -r requirements.txt`.
3.  На [Google Cloud](https://console.cloud.google.com/apis) создайте проект
    + На вкладке APIs & Services добавьте **Google Drive Api** и  **Google Sheets API**
    + Перейдите в секцию **[Credentials](https://console.cloud.google.com/apis/credentials)** и при создание выберите **Service Account**
    + После создания выберите созданный аккаунт, перейдите во вкладку **Keys**, создайте ключ в формате JSON
    + Поместите в папку с программой
4. Создайте файл `.env` по примеру `.env.example`. Заполните все переменные
5. Запустите приложение, выполнив `fastapi dev main.py`.