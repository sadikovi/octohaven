-- run: mysql -u root -p < setup.sql
-- global
\. mysql/global.ddl
-- tables
\. mysql/users.ddl
\. mysql/projects.ddl
\. mysql/branches.ddl
\. mysql/modules.ddl
\. mysql/components.ddl
-- revisions
\. mysql/branch_revisions.ddl
\. mysql/module_revisions.ddl
-- connections
\. mysql/branch_module.ddl
