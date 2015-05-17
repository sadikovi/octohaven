-- Branches table (Project -> Branch)
drop table if exists octohaven.branches;
-- create branches table
create table octohaven.branches (
    uniqueid int(8) unsigned auto_increment primary key,
    userid int(8) unsigned,
    projectid int(8) unsigned,
    id varchar(255),
    created datetime
) engine = InnoDB, comment = 'Branches global info';
-- done comment
SELECT '<Branches table is created>' AS ' ';

-- create index for projectid, userid, id
create unique index UIX_PROJECT_USER_BRANCH on octohaven.branches(userid, projectid, id);
-- done comment
SELECT '<Unique index for branches table is created>' AS ' ';
