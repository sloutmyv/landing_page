# Docker Compose Commands

## Build and start containers
docker-compose up --build

## Start containers in detached mode
docker-compose up -d

## Stop containers
docker-compose down

## View logs
docker-compose logs -f

## Run migrations
docker-compose exec web python manage.py migrate

## Create superuser
docker-compose exec web python manage.py createsuperuser

## Access Django shell
docker-compose exec web python manage.py shell

## Rebuild containers
docker-compose up --build --force-recreate
