# Makefile

# Ortam Değişkenleri
POSTGRES_USER=admin
POSTGRES_PASSWORD=password
POSTGRES_DB=db
POSTGRES_PORT=5432
SQL_FILE=tables.sql

.PHONY: up down

# Servisleri Başlat
up:
	POSTGRES_USER=$(POSTGRES_USER) \
	POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
	POSTGRES_DB=$(POSTGRES_DB) \
	POSTGRES_PORT=$(POSTGRES_PORT) \
	SQL_FILE=$(SQL_FILE) \
	docker-compose up -d

connect:
	docker exec -it my_postgres psql -U admin -d db -p 5432

# Servisleri Durdur ve Volume'leri Sil
down:
	docker-compose down -v