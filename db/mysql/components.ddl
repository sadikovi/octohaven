-- Components table (Project -> Branch -> Module -> Component)
drop table if exists octohaven.components;
create table octohaven.components (
    uniqueid int(8) unsigned auto_increment primary key,
    userid int(8) unsigned,
    id varchar(255),
    type varchar(255),
    fileurl varchar(255),
    created datetime
) engine = InnoDB, comment = 'Components table';
-- done comment
SELECT '<Components table is created>' AS ' ';

-- create unique index on component name
create unique index UIX_COMPONENT_USERID_ID_TYPE on octohaven.components(userid, id, type);
-- done comment
SELECT '<Unique index for components table is created>' AS ' ';
