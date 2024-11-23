include .env

up:
	docker-compose up -d

connect:
	docker exec -it my_postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -p $(POSTGRES_PORT)

down:
	docker-compose down -v
