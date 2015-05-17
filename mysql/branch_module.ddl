-- Branch module relation
drop table if exists octohaven.branch_module;
-- create table
create table octohaven.branch_module (
    branch_revision_id int(8) unsigned,
    module_revision_id int(8) unsigned
) engine = InnoDB, comment = 'Branch-Module table';

-- done comment
SELECT '<Branch-Module table is created>' AS ' ';

-- ? create index on branch_revision_id
