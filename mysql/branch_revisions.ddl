-- Branch revisions (saves)
drop table if exists octohaven.branch_revisions;
-- create table
create table octohaven.branch_revisions (
    revision_id int(8) unsigned auto_increment primary key,
    branchid int(8) unsigned,
    created datetime,
    latest tinyint(1)
) engine = InnoDB, comment = 'Branch revisions';

-- done comment
SELECT '<Branch revisions table is created>' AS ' ';

-- create index on branch id
create index IX_BRANCHID on octohaven.branch_revisions (branchid);
-- done comment
SELECT '<Index for branch revisions table is created>' AS ' ';
