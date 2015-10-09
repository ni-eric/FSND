-- Table definitions for the tournament project.

-- create new database and connect to it
DROP DATABASE IF EXISTS tournament;


CREATE DATABASE tournament;

 \c tournament;

-- create players and matches table
CREATE TABLE players(
	id serial PRIMARY KEY, 
	name text);


CREATE TABLE matches(
	id serial PRIMARY KEY, 
	winner int REFERENCES players, 
	loser int REFERENCES players);


-- wincount queries number of wins for each player 
CREATE VIEW wincount AS
SELECT players.id,

  (SELECT COUNT(*)
   FROM matches
   WHERE players.id = matches.winner) AS num
FROM players;


-- matchcount queries number of matches played by each player 
CREATE VIEW matchcount AS
SELECT players.id,

  (SELECT COUNT(*)
   FROM matches
   WHERE players.id = matches.winner
     OR players.id = matches.loser) AS num
FROM players;


-- OMW = 'opponent match wins': the total #wins by opponents of each player
CREATE VIEW omw AS
SELECT players.id,
  (SELECT SUM(wincount.num)
   FROM (
           (SELECT matches.winner AS id
            FROM matches
            WHERE players.id=matches.loser)
         UNION
           (SELECT matches.loser AS id
            FROM matches
            WHERE players.id=matches.winner)) AS opponent,
        wincount
   WHERE wincount.id=opponent.id)
FROM players;


-- standings shows #wins and #matches for each player
-- players are ranked first by #wins, and then by OMW
CREATE VIEW standings AS
SELECT players.id,
       players.name,
       wincount.num AS wins,
       matchcount.num AS matches
FROM players,
     wincount,
     matchcount,
     omw
WHERE players.id=wincount.id
  AND players.id=matchcount.id
  AND players.id=omw.id
ORDER BY wins DESC, omw.sum DESC;


