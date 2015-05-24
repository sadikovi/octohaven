-- run: mysql -u root -p < setup.sql
-- global
\. db/mysql/global.ddl
-- tables
\. db/mysql/users.ddl
\. db/mysql/projects.ddl
\. db/mysql/branches.ddl
\. db/mysql/modules.ddl
\. db/mysql/components.ddl
-- revisions
\. db/mysql/branch_revisions.ddl
\. db/mysql/module_revisions.ddl
-- connections
\. db/mysql/branch_module.ddl
