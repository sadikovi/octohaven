-- Projects table
drop table if exists octohaven.projects;
create table octohaven.projects (
    id int(8) unsigned auto_increment primary key,
    name varchar(255),
    created datetime,
    branch int(8) unsigned,
    owner varchar(255),
    is_deleted tinyint(1) default 0
) engine = InnoDB, comment = 'Projects global info';

-- done comment
SELECT '<Projects table is created>' AS ' ';
