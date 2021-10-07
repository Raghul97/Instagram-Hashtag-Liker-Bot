# Instagram Hashtag Liker Bot.

Fully dockerized automated instagram post liker bot with user credentials and hashtags using flask, celery, redis, mongodb, selenium.

## structure

.
├── celery_worker
│   ├── Dockerfile
│   ├── instagram
│   │   ├── bots.py
│   │   ├── __init__.py
│   │   ├── login.py
│   │   └── utils.py
│   ├── requirements.freeze
│   └── tasks.py
├── docker-compose.yml
├── flask_app
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.freeze
│   ├── static
│   │   ├── scripts
│   │   │   ├── bot_status.js
│   │   │   └── index.js
│   │   └── styles
│   │       ├── bot.css
│   │       └── index.css
│   └── templates
│       ├── bot_status.html
│       └── index.html
└── README.md

7 directories, 18 files

## Software used in this project.

1. Flask
2. Celery
3. redis
4. MongoDB
5. selenium

## Software required to run.

1. Docker

## command to start application.

1. run the following command at root directory, where docker-compose.yml file exists.

	docker-compose up
	
## what and how it does?

1. The client enters the username, password and hashtags (seperated by commas) which he wants the bot to like.

2. flask parses this application and starts a async task with celery and redis as messaging queue and also starts the async countdown for the total period of execution.

3. this async task triggers web scrapper using selenium to collect the posts data of particular hashtag mentioned by the user.

4. once the required amount of posts details are collected, another set of web scrapper using selenium is launched to navigate to the posts url and like the post, if it is not already liked.


