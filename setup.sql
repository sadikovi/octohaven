-- run: mysql -u root -p < setup.sql
-- global
\. mysql/global.sql
-- tables
\. mysql/users.sql
\. mysql/projects.sql
\. mysql/branches.sql
\. mysql/modules.sql
\. mysql/components.sql
-- revisions
\. mysql/branch_revisions.sql
\. mysql/module_revisions.sql
