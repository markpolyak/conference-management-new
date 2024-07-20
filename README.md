# conference-management-new

## Бэкенд. Работа с заявками

### Подключение к Google Sheets

Для подключения к Google Sheets требуется выполнить инструкцию с сайта [документации gspread](https://docs.gspread.org/en/latest/oauth2.html#enable-api-access) для google service account 

### Подключение Google SMPT

Для подключения надо: 
- Добавить почту в переменную **smtp-server-mail** файла конфигурации почту, с которой будут отправляться сообщения 
- Пароль приложений google в переменную **smtp-server-password** файла конфигурации 

Для получения пароля приложений google требуется:
1) Зайти в свою почту google и нажать на "Управление аккаунтом Google" в верхнем правом углу
2) Включить 2ух-факторную аутентификацию на аккаунте
3) В поиске в верхней части экранна ввести "Пароли приложений" и перейти в соответствующую вкладку темы "Безопасность"
4) Ввести название приложения, нажать кнопку "Создать"
5) Скопировать пароль (Пароль показывается только один раз)

### Файл конфигурации

Файл конфигурации должен быть расположен в папке %appdata%/conferences/config.yml

Как должен выглядеть yaml

````yaml

conferences-sheet-id: 'id таблицы'
smtp-server-mail: почта
smtp-server-password: 'пароль google приложений'

````