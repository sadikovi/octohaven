-- Components table (Project -> Branch -> Module -> Component)
drop table if exists octohaven.components;
create table octohaven.components (
    revision_id int(8) unsigned auto_increment primary key,
    name varchar(255),
    type varchar(255),
    fileurl varchar(255),
    extension varchar(255),
    description varchar(255),
    created datetime,
    latest tinyint(1) default 1
) engine = InnoDB, comment = 'Components table';
-- done comment
SELECT '<Components table is created>' AS ' ';

-- create unique index on component name
create unique index UIX_COMPONENT_NAME on octohaven.components(name);
-- done comment
SELECT '<Unique index for components table is created>' AS ' ';
