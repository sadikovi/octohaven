-- Branches table (Project -> Branch)
drop table if exists octohaven.branches;
create table octohaven.branches (
    id int(8) unsigned auto_increment primary key,
    name varchar(255),
    created datetime,
    project int(8) unsigned,
    owner varchar(255),
    is_deleted tinyint(1) default 0
) engine = InnoDB, comment = 'Branches global info';

-- done comment
SELECT '<Branches table is created>' AS ' ';
