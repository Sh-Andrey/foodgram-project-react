![foodgram workflow](https://github.com/evi1ghost/foodgram-project-react/workflows/foodgram_workflow/badge.svg)

##Дипломный проект по курсу Python-разработчик от Яндекс.Практикума — «Продуктовый помощник».
## Краткое описание.
Приложение для публикации рецептов различных блюд. Пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис "Список покупок" позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Стек технологий.
Python3, Django 3, Django REST Framework, PostgreSQL,
CI/CD, Docker, Nginx, YandexCloud

## Запуск проекта
### Установить Docker и Docker-compose:
Для работы с проектом должен быть установлен Docker и docker-compose. Эта команда скачает скрипт для установки докера:
```
curl -fsSL https://get.docker.com -o get-docker.sh
```
Эта команда запустит его:
```
sh get-docker.sh
```
Установка docker-compose:
```
sudo apt install docker-compose
```

### Склонировать проекст с GitHub:
```
git@github.com:Sh-Andrey/foodgram-project-react.git
```

### Перейти в папку infra и создать файл .env по образцу .env.example.
```
SECRET_KEY=' '
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=foodgram
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
DEBUG=False
HOSTS_LIST=127.0.0.1, localhost
```
### Запуск контейнеров:
- Перейдите в папку infra и запустите команду:
```
sudo docker-compose up -d
```
- После сборки всех контейнеров нужно запустить скрип install.sh:
```
docker-compose exec backend bash install.sh
```
### Проект запущен:
```
http://<ip>/
```
### Документация:
```
http://<ip>/api/docs/
```

### Уже развернутый проект можно посмотреть по ссылке:
```
http:// /
```

## Использование CI/CD:
Для использования Continuous Integration и Continuous Deployment необходимо в репозитории на GitHub прописать Secrets - переменные доступа к вашим сервисам. Переменые прописаны в workflows/yamdb_workflow.yaml:
```
SECRET_KEY=' '
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=foodgram
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
DEBUG=False / True
HOSTS_LIST=127.0.0.1, localhost

DOCKER_PASSWORD=<пароль DockerHub>
DOCKER_USERNAME=<имя пользователя DockerHub>

USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

TELEGRAM_TO=<ID своего телеграм-аккаунта>
TELEGRAM_TOKEN=<токен вашего бота>
```