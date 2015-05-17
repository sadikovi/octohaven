-- Branches table (Project -> Branch)
drop table if exists octohaven.branches;
-- create branches table
create table octohaven.branches (
    branchid int(8) unsigned auto_increment primary key,
    projectid varchar(255),
    userid varchar(255),
    id varchar(255),
    created datetime,
    is_deleted tinyint(1) default 0
) engine = InnoDB, comment = 'Branches global info';
-- done comment
SELECT '<Branches table is created>' AS ' ';

-- create index for projectid, userid, id
create unique index UIX_PROJECT_USER_BRANCH on octohaven.branches(projectid, userid, id);
-- done comment
SELECT '<Unique index on branches table is created>' AS ' ';
