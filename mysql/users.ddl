-- Users table
drop table if exists octohaven.users;
create table octohaven.users (
    uniqueid int(8) unsigned auto_increment primary key,
    id varchar(255),
    pass varchar(255),
    created datetime
) engine = InnoDB, comment = 'Users global info';
-- done comment
SELECT '<Users table is created>' AS ' ';

-- create unique index on user id
create unique index UIX_USER_ID on octohaven.users(id);
-- done comment
SELECT '<Unique index for users table is created>' AS ' ';
