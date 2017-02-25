-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE TABLE players (PlayerID SERIAL, Name TEXT, 
					  Wins INT, Match INT, Standing INT, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
