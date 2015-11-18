DROP DATABASE IF EXISTS catalog;


CREATE DATABASE catalog;

 \c catalog;

CREATE TABLE items(
	id serial PRIMARY KEY,
	name text,
	category text,
	description text);

CREATE TABLE users(
	id serial PRIMARY KEY,
	name, text);