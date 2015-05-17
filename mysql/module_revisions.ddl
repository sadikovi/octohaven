-- Module revisions (saves)
drop table if exists octohaven.module_revisions;
create table octohaven.module_revisions (
    revision_id int(8) unsigned auto_increment primary key,
    id int(8) unsigned,
    created datetime,
    content blob,
    latest tinyint(1)
) engine = InnoDB, comment = 'Module revisions';

-- done comment
SELECT '<Module revisions table is created>' AS ' ';
