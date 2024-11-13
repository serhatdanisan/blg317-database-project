CREATE DATABASE db
USE db

CREATE TABLE club (
	id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    officialname VARCHAR(150) NOT NULL,
    country VARCHAR(50) NOT NULL,
    venue_id INT,
    FOREIGN KEY (venue_id) REFERENCES football_stadiums(id)
);

CREATE TABLE match(
	id INT PRIMARY KEY,
    dateutc DATETIME NOT NULL,
    competition VARCHAR(100) NOT NULL,
    venue_id INT,
    home_club VARCHAR(20) NOT NULL,
    away_club VARCHAR(20) NOT NULL,
    winner VARCHAR(20) NOT NULL,
    goal_by_home_club INT NOT NULL,
    goal_by_away_club INT NOT NULL
    FOREIGN KEY (venue_id) REFERENCES football_stadiums(id)
);

