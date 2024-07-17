#Заполнение cfg.py

SPREADSHEET_ID - ID родительской гугл таблицы
ORG_BOT = токен телеграм бота для организаторов конференций
USER_BOT = токен телеграм бота для участников конференций
ACCESS_EMAIL - email, который будет иметь доступ ко всем дочерним таблицам

токены для телеграмм ботов получаются из https://t.me/BotFather

Перед запуском бота для работы с гугл таблицами требуется заменить файл creds-example.json на creds.json, полученный при создании апи на https://console.cloud.google.com/apis

#Детали доступа
В ходе работы сервисным аккаунтом, полученным при регистрации апи, будут создаваться дочерние таблицы. Права на владение передаются аккаунты, указанному в cfg.py -> ACCESS_EMAIL. Дальнейшее администрирование таблиц будет доступно ему. Все созданные таблицы хранятся на гугл диске аккаунты, который создавал апи ключи