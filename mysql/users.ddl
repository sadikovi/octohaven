-- Users table
drop table if exists octohaven.users;
create table octohaven.users (
    id varchar(255),
    created datetime,
    primary key (id)
) engine = InnoDB, comment = 'Users global info';

-- done comment
SELECT '<Users table is created>' AS ' ';
