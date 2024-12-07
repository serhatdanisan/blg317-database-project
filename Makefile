include .env

up:
	docker-compose up --build

connect:
	docker exec -it blg317-database-project-db-1 -U $(POSTGRES_USER) -d $(POSTGRES_DB) -p $(POSTGRES_PORT)

down:
	docker-compose down -v
