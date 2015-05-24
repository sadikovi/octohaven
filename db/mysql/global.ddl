-- Global settings
-- creating database
drop database if exists octohaven;
create database octohaven;
SELECT '<Database is created>' AS ' ';

-- create user
drop user 'octohaven_user'@'%';
create user 'octohaven_user'@'%' identified by 'octohaven';
SELECT '<User is created>' AS ' ';
-- ...and set grants
grant select, insert, update, delete, create, drop on octohaven.* to 'octohaven_user'@'%';
SELECT '<Grants are set for user>' AS ' ';
