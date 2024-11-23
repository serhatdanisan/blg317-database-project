CREATE TABLE IF NOT EXISTS "club" (
	"id" serial NOT NULL UNIQUE,
	"name" varchar(255),
	"officialname" varchar(255),
	"country" varchar(255),
	"stadiums_id" bigint,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "player" (
	"id" serial NOT NULL UNIQUE,
	"firstname" varchar(255),
	"lastname" varchar(255),
	"birthdate" varchar(255),
	"country_id" bigint,
	"position" varchar(255),
	"foot" varchar(255),
	"height" smallint,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "football_match" (
	"id" serial NOT NULL UNIQUE,
	"dateutc" varchar(255),
	"competition" varchar(255),
	"season" smallint,
	"stadiums_id" bigint NOT NULL,
	"home_club" varchar(255),
	"away_club" varchar(255),
	"winner" varchar(255),
	"goal_by_home_club" smallint,
	"goal_by_away_club" smallint,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "football_match_event" (
	"id" serial NOT NULL UNIQUE,
	"club_id" bigint,
	"football_match_id" bigint,
	"player_id" bigint,
	"matchperiod" varchar(255),
	"eventsec" varchar(255),
	"eventname" varchar(255),
	"action" varchar(255),
	"modifier" varchar(255),
	"x_begin" smallint,
	"y_begin" smallint,
	"x_end" float,
	"y_end" float,
	"is_success" boolean,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "countries" (
	"id" serial NOT NULL UNIQUE,
	"country" varchar(255),
	"capital_city" varchar(255),
	"region" varchar(255),
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "stadiums" (
	"id" serial NOT NULL UNIQUE,
	"confederation" varchar(255),
	"stadium" varchar(255),
	"city" varchar(255),
	"capacity" bigint,
	"country_id" bigint,
	PRIMARY KEY ("id")
);

ALTER TABLE "club" ADD CONSTRAINT "club_fk4" FOREIGN KEY ("stadiums_id") REFERENCES "stadiums"("id");

ALTER TABLE "player" ADD CONSTRAINT "player_fk4" FOREIGN KEY ("country_id") REFERENCES "countries"("id");

ALTER TABLE "football_match" ADD CONSTRAINT "football_match_fk4" FOREIGN KEY ("stadiums_id") REFERENCES "stadiums"("id");

ALTER TABLE "football_match_event" ADD CONSTRAINT "football_match_event_fk1" FOREIGN KEY ("club_id") REFERENCES "club"("id");

ALTER TABLE "football_match_event" ADD CONSTRAINT "football_match_event_fk2" FOREIGN KEY ("football_match_id") REFERENCES "football_match"("id");

ALTER TABLE "football_match_event" ADD CONSTRAINT "football_match_event_fk3" FOREIGN KEY ("player_id") REFERENCES "player"("id");

ALTER TABLE "stadiums" ADD CONSTRAINT "stadiums_fk5" FOREIGN KEY ("country_id") REFERENCES "countries"("id");





COPY countries FROM '/data/csv_files/countries.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true);
COPY stadiums FROM '/data/csv_files/stadiums.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true);
COPY club FROM '/data/csv_files/club.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true);
COPY player FROM '/data/csv_files/player.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true);
COPY football_match FROM '/data/csv_files/football_match.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true);
COPY football_match_event FROM '/data/csv_files/football_match_event.csv' WITH (FORMAT csv, DELIMITER ',', HEADER true);