-- Projects table
drop table if exists octohaven.projects;
create table octohaven.projects (
    uniqueid int(8) unsigned auto_increment primary key,
    userid int(8) unsigned,
    id varchar(255),
    created datetime
) engine = InnoDB, comment = 'Projects global info';
-- done comment
SELECT '<Projects table is created>' AS ' ';

-- create unique index on user id
create unique index UIX_PROJECT_ID on octohaven.projects(userid, id);
-- done comment
SELECT '<Unique index for projects table is created>' AS ' ';
