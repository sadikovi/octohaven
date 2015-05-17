-- Projects table
drop table if exists octohaven.projects;
create table octohaven.projects (
    id varchar(255),
    userid varchar(255),
    created datetime
    primary key (id, userid)
) engine = InnoDB, comment = 'Projects global info';

-- done comment
SELECT '<Projects table is created>' AS ' ';
