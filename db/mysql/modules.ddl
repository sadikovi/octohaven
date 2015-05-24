-- Modules table (Project -> Branch -> Module)
drop table if exists octohaven.modules;
create table octohaven.modules (
    id int(8) unsigned auto_increment primary key,
    created datetime
) engine = InnoDB, comment = 'Modules global info';

-- done comment
SELECT '<Modules table is created>' AS ' ';
