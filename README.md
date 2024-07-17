
Для подключения бота к бэкенду необходимо в файле main.py в корневой директории: 
1. Расскоментировать блоки кода, которые имеют комментарий "TODO: бэкенд". Данные блоки 	
	ограничены сверху комментарием # TODO: бэкенд, снизу ограничены набором символов ######.
	Например, первый такой блок выглядит так:
	
		# TODO: бэкенд
    	# active_conferences = fetch_all_conferences('active')
    	# filtered_past_conferences = fetch_past_conferences_with_applications(message)
    	###############################
    	
2. Закомментировать блоки кода, которые имеют комментарий "TODO: эмуляция". Выделение
    	блоков такое же, как и в первом пункте
***
В файле config.py в директории config необходимо указать две константы: 
1. TOKEN - токен telegram-бота 
2. base_http - url для подключения к бэкенду
***
Для запуска бота необходимо ввести команды: 
1. sudo docker build -t orlov_participants_bot .
2. sudo docker run --name orlov_bot orlov_participants_bot

