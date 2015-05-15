-- Users table
drop table if exists octohaven.users;
create table octohaven.users (
    name varchar(255) primary key,
    created datetime,
    is_deleted tinyint(1) default 0
) engine = InnoDB, comment = 'Users global info';

-- done comment
SELECT '<Users table is created>' AS ' ';
