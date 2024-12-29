CREATE TABLE IF NOT EXISTS "countries" (
    "id" SERIAL PRIMARY KEY,
    "country" VARCHAR(255) NOT NULL,
    "capital_city" VARCHAR(255),
    "region" VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS "stadiums" (
    "id" SERIAL PRIMARY KEY,
    "confederation" VARCHAR(255),
    "stadium" VARCHAR(255) NOT NULL,
    "city" VARCHAR(255) NOT NULL,
    "capacity" BIGINT CHECK (capacity > 0),
    "country_id" INT REFERENCES "countries"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "club" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "officialname" VARCHAR(255),
    "country" VARCHAR(255),
    "stadiums_id" INT REFERENCES "stadiums"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "player" (
    "id" SERIAL PRIMARY KEY,
    "firstname" VARCHAR(255) NOT NULL,
    "lastname" VARCHAR(255) NOT NULL,
    "birthdate" DATE,
    "country_id" INT REFERENCES "countries"("id") ON DELETE SET NULL ON UPDATE CASCADE,
    "position" VARCHAR(255),
    "foot" VARCHAR(50),
    "height" SMALLINT
);

CREATE TABLE IF NOT EXISTS "football_match" (
    "id" SERIAL PRIMARY KEY,
    "dateutc" TIMESTAMP NOT NULL,
    "competition" VARCHAR(255),
    "season" SMALLINT CHECK (season >= 1900),
    "stadiums_id" INT REFERENCES "stadiums"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "home_club" INT REFERENCES "club"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "away_club" INT REFERENCES "club"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "winner" INT REFERENCES "club"("id") ON DELETE SET NULL ON UPDATE CASCADE,
    "goal_by_home_club" SMALLINT CHECK (goal_by_home_club >= 0),
    "goal_by_away_club" SMALLINT CHECK (goal_by_away_club >= 0)
);

CREATE TABLE IF NOT EXISTS "football_match_event" (
    "id" SERIAL PRIMARY KEY,
    "club_id" INT REFERENCES "club"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "football_match_id" INT REFERENCES "football_match"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "player_id" INT REFERENCES "player"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "matchperiod" VARCHAR(50),
    "eventsec" FLOAT CHECK (eventsec >= 0),
    "eventname" VARCHAR(255),
    "action" VARCHAR(255),
    "modifier" VARCHAR(255),
    "x_begin" SMALLINT CHECK (x_begin >= 0),
    "y_begin" SMALLINT CHECK (y_begin >= 0),
    "x_end" FLOAT CHECK (x_end >= 0),
    "y_end" FLOAT CHECK (y_end >= 0),
    "is_success" BOOLEAN
);

CREATE TABLE IF NOT EXISTS "users" (
    "user_id" SERIAL PRIMARY KEY,
    "username" VARCHAR,
    "psw" VARCHAR,
    "email" VARCHAR(255) UNIQUE,
    "user_role" INT DEFAULT 0
);


CREATE INDEX idx_country_name ON countries(country);
CREATE INDEX idx_stadium_country_id ON stadiums(country_id);
CREATE INDEX idx_club_stadiums_id ON club(stadiums_id);
CREATE INDEX idx_player_country_id ON player(country_id);
CREATE INDEX idx_football_match_stadiums_id ON football_match(stadiums_id);
CREATE INDEX idx_event_football_match_id ON football_match_event(football_match_id);

COPY countries FROM '/data/csv_files/countries.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true);
COPY stadiums FROM '/data/csv_files/stadiums.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true);
COPY club FROM '/data/csv_files/club.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true);
COPY player FROM '/data/csv_files/player.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true);
COPY football_match FROM '/data/csv_files/football_match.csv' WITH (FORMAT csv, DELIMITER ',', HEADER true);
COPY football_match_event FROM '/data/csv_files/football_match_event.csv' WITH (FORMAT csv, DELIMITER ',', HEADER true);

SELECT setval('countries_id_seq', (SELECT MAX(id) FROM countries));
SELECT setval('stadiums_id_seq', (SELECT MAX(id) FROM stadiums));
SELECT setval('club_id_seq', (SELECT MAX(id) FROM club));
SELECT setval('player_id_seq', (SELECT MAX(id) FROM player));
SELECT setval('football_match_id_seq', (SELECT MAX(id) FROM football_match));
SELECT setval('football_match_event_id_seq', (SELECT MAX(id) FROM football_match_event));

