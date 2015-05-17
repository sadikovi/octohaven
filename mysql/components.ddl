-- Components table (Project -> Branch -> Module -> Component)
drop table if exists octohaven.components;
create table octohaven.components (
    id int(8) unsigned auto_increment primary key,
    type varchar(255),
    fileurl varchar(255),
    extension varchar(255),
    description varchar(255),
    created datetime,
    is_deleted tinyint(1)
) engine = InnoDB, comment = 'Components table';

-- done comment
SELECT '<Components table is created>' AS ' ';
