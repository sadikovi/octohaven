#!/usr/bin/env python

# mysql settings
mysql_host = "localhost"
mysql_user = "octohaven_user"
mysql_pass = "octohaven"

# global
db_schema = "octohaven"
# users table
db_table_users = "users"
# user table columns
db_table_users_uniqueid = "uniqueid"
db_table_users_id = "id"
db_table_users_created = "created"

# projects table
db_table_projects = "projects"
# projects table columns
db_table_projects_uniqueid = "uniqueid"
db_table_projects_userid = "userid"
db_table_projects_id = "id"
db_table_projects_created = "created"

# branches table
db_table_branches = "branches"
# branches table columns
db_table_branches_uniqueid = "uniqueid"
db_table_branches_userid = "userid"
db_table_branches_projectid = "projectid"
db_table_branches_id = "id"
db_table_branches_created = "created"

# modules table
db_table_modules = "modules"
# modules table columns
db_table_modules_id = "id"
db_table_modules_created = "created"

# components table
db_table_components = "components"
# components table columns
db_table_components_uniqueid = "uniqueid"
db_table_components_userid = "userid"
db_table_components_id = "id"
db_table_components_type = "type"
db_table_components_fileurl = "fileurl"
db_table_components_created = "created"

# branch revisions
db_table_branch_rev = "branch_revisions"
# branch revisions columns
db_table_branch_rev_revisionid = "revision_id"
db_table_branch_rev_branchid = "branchid"
db_table_branch_rev_created = "created"
db_table_branch_rev_latest = "latest"
