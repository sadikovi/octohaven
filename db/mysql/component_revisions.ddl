-- Component revisions table
drop table if exists octohaven.component_revisions;
create table octohaven.component_revisions (
    revision_id int(8) unsigned auto_increment primary key,
    componentid int(8) unsigned,
    description varchar(255),
    created datetime,
    latest tinyint(1) default 1
) engine = InnoDB, comment = 'Component revisions';
-- done comment
SELECT '<Component revisions table is created>' AS ' ';

-- create unique index on component name
create unique index UIX_COMPONENT_ID on octohaven.component_revisions(componentid);
-- done comment
SELECT '<Unique index for component revisions table is created>' AS ' ';
