-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE DATABASE tournament;

CREATE TABLE players (PlayerID SERIAL PRIMARY KEY, Name TEXT, 
					  Wins INT, Match INT);

CREATE TABLE matches (matchID SERIAL PRIMARY KEY, winnerID INT REFERENCES players(playerID),
					  loserID INT REFERENCES players(playerID));

CREATE OR REPLACE VIEW playerRankings AS SELECT PlayerID, name,
Rank() OVER(ORDER BY Wins DESC), Row_number() OVER(ORDER BY Wins DESC), Wins FROM players;

CREATE OR REPLACE VIEW evenRows AS SELECT PlayerID, name, Rank() OVER(ORDER BY Wins DESC),
Row_number() OVER(ORDER BY Wins DESC), Wins FROM playerRankings WHERE mod(row_number,2)=0;

CREATE OR REPLACE VIEW oddRows AS SELECT PlayerID, name, Rank() OVER(ORDER BY Wins DESC),
Row_number() OVER(ORDER BY Wins DESC), Wins FROM playerRankings WHERE mod(row_number,2)=1;

CREATE OR REPLACE VIEW pairings AS SELECT oddRows.playerID AS p1, oddRows.name AS p1_Name, 
                evenRows.playerID AS p2, evenRows.name AS p2_Name FROM oddRows, evenRows
                WHERE oddRows.row_number = evenRows.row_number;