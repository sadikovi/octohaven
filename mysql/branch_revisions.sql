-- Branch revisions (saves)
drop table if exists octohaven.branch_revisions;
create table octohaven.branch_revisions (
    revision_id int(8) unsigned auto_increment primary key,
    id int(8) unsigned,
    created datetime,
    modules blob,
    latest tinyint(1)
) engine = InnoDB, comment = 'Branch revisions';

-- done comment
SELECT '<Branch revisions table is created>' AS ' ';
