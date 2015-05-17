-- Module revisions (saves)
drop table if exists octohaven.module_revisions;
create table octohaven.module_revisions (
    revision_id int(8) unsigned auto_increment primary key,
    moduleid int(8) unsigned,
    created datetime,
    content blob,
    latest tinyint(1)
) engine = InnoDB, comment = 'Module revisions';
-- done comment
SELECT '<Module revisions table is created>' AS ' ';

-- create index on branch id
create index IX_MODULE_ID on octohaven.module_revisions (moduleid);
-- done comment
SELECT '<Index for module revisions table is created>' AS ' ';
