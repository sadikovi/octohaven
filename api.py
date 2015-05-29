#!/usr/bin/env python

# import libs
from google.appengine.api import users
import webapp2
import urllib2
import re
import json
import _paths
from src.redis.core import Project, Branch
from src.netutils import APIResult, APIResultStatusSuccess, APIResultStatusWarning
from src.netutils import APIResultStatusError400, APIResultStatusError401
from src.netutils import APIResultStatusError500
from src.netutils import JSON
from src.redis.errors import CoreError
import src.redis.config as config
from src.redis.manager import Manager
from src.connector.redisconnector import RedisConnectionPool, RedisConnector

# init pool
octohaven_pool = RedisConnectionPool(config.settings)

def manager():
    rc = RedisConnector(poolhandler=octohaven_pool)
    return Manager(connector=rc)

PROJECT_CREATE = "create"
PROJECT_UPDATE = "update"
PROJECT_DELETE = "delete"
PROJECT_VALIDATE = "validate"
PROJECT_ACTION_URL = "/api/project/(%s|%s|%s|%s)"%(PROJECT_CREATE, PROJECT_UPDATE, PROJECT_DELETE, PROJECT_VALIDATE)

# create new project
class api_project_action(webapp2.RequestHandler):
    def post(self, *args):
        user, result = users.get_current_user(), None
        if not user:
            result = APIResult(APIResultStatusError401(), "Not authenticated. Please re-login")
        else:
            # extract action
            action = "%s"%(args[0]) if args else None
            data = self.request.body.strip()
            data = JSON.safeloads(data, unquote=True, strip=True, lower=True)
            pnamekey, pdesckey = "projectname", "projectdesc"
            # perform check
            pname = data[pnamekey] if pnamekey in data else None
            pdesc = data[pdesckey] if pdesckey in data else None
            result = self.performAction(action, user.user_id(), pname, pdesc)
            # something is wrong with workflow
            if not result:
                result = APIResult(APIResultStatusError500(), "Workflow issues. Try again later")
        # send request
        self.response.headers["Content-Type"] = "application/json"
        self.response.set_status(result.code())
        self.response.out.write(json.dumps(result.dict()))

    def performAction(self, action, userid, pname, pdesc):
        if action not in [PROJECT_CREATE, PROJECT_UPDATE, PROJECT_DELETE, PROJECT_VALIDATE]:
            return APIResult(APIResultStatusError400(), "Project action is not recognized")
        # else parse data and perform action
        try:
            mngr = manager()
            puser = mngr.getUser(userid)
            if not puser:
                raise CoreError("Requested user does not exist. Please re-login")
            puserhash, result = puser.hash(), None
            projectgroup = mngr.getProjectGroup(puser.hash())
            if action == PROJECT_CREATE:
                pname = Project.validateName(pname)
                projectgroup.addProject(pname, pdesc)
                data = { "redirect": "/project/%s"%(pname), "isnew": True }
                result = APIResult(APIResultStatusSuccess(), "All good", data)
            elif action == PROJECT_UPDATE:
                pname = Project.validateName(pname)
                projectgroup.updateDesc(pname, pdesc)
            elif action == PROJECT_DELETE:
                pname = Project.validateName(pname)
                projectgroup.removeProject(pname)
            elif action == PROJECT_VALIDATE:
                Project.validateName(pname)
            else:
                pass
            # everything is ok, requires standard ok message
            if not result:
                result = APIResult(APIResultStatusSuccess(), "All good")
            mngr.updateProjectGroup(projectgroup)
        except CoreError as ce:
            return APIResult(APIResultStatusError400(), ce._msg)
        except:
            return APIResult(APIResultStatusError400(), "General error occuried. Try again later")
        else:
            return result


BRANCH_CREATE = "create"
BRANCH_DEFAULT = "default"
BRANCH_DELETE = "delete"
BRANCH_SELECT = "select"
BRANCH_ACTION_URL = "/api/branch/(%s|%s|%s|%s)"%(BRANCH_CREATE, BRANCH_DELETE, BRANCH_DEFAULT, BRANCH_SELECT)

class api_branch_action(webapp2.RequestHandler):
    def post(self, *args):
        user, result = users.get_current_user(), None
        if not user:
            result = APIResult(APIResultStatusError401(), "Not authenticated. Please re-login")
        else:
            # extract action
            action = "%s"%(args[0]) if args else None
            data = JSON.safeloads(self.request.body.strip(), unquote=True, strip=True, lower=True)
            phashkey, pidkey, bidkey = "projecthash", "projectname", "branchname"
            # perform check
            projecthash = data[phashkey] if phashkey in data else None
            projectname = data[pidkey] if pidkey in data else None
            branchname = data[bidkey] if bidkey in data else None
            result = self.performBranchAction(action, user.user_id(), projecthash, projectname, branchname)
            # something is wrong with workflow
            if not result:
                result = APIResult(APIResultStatusError500(), "Workflow issues. Try again later")
        # send request
        self.response.headers["Content-Type"] = "application/json"
        self.response.set_status(result.code())
        self.response.out.write(json.dumps(result.dict()))

    def performBranchAction(self, action, userid, projecthash, projectname, branchname):
        if action not in [BRANCH_CREATE, BRANCH_DELETE, BRANCH_DEFAULT, BRANCH_SELECT]:
            return APIResult(APIResultStatusError400(), "Branch action is not recognized")
        try:
            mngr = manager()
            puser = mngr.getUser(userid)
            if not puser:
                raise CoreError("Requested user does not exist. Please re-login")
            # [!] fix it: request project group
            projectgroup = mngr.getProjectGroup(puser.hash())
            project = projectgroup.project(projectname)
            if not project:
                raise CoreError("Project {%s} is not recognized"%(projectname))
            # request branch group
            branchgroup = mngr.getBranchGroup(puser.hash(), project.hash())
            # do action
            if action == BRANCH_CREATE:
                branchname = Branch.validateName(branchname)
                branchgroup.addBranch(branchname)
            elif action == BRANCH_DEFAULT:
                branchname = Branch.validateName(branchname)
                branchgroup.setDefault(branchname)
            elif action == BRANCH_DELETE:
                branchname = Branch.validateName(branchname)
                branchgroup.removeBranch(branchname)
            else:
                pass
            mngr.updateBranchGroup(branchgroup)
            # convert into objects list
            llist = []
            for x in branchgroup.branches():
                lobj = {
                    "name": x.name(),
                    "default": x.default(),
                    "edited": x.edited(),
                    "link": "/project/%s/branch/%s"%(project.name(), x.name())
                }
                llist.append(lobj)
            data = { "branches": sorted(llist, cmp=lambda x, y: cmp(x["edited"], y["edited"]), reverse=True) }
            return APIResult(APIResultStatusSuccess(), "All good", data)
        except CoreError as ce:
            return APIResult(APIResultStatusError400(), ce._msg)
        except:
            return APIResult(APIResultStatusError400(), "General error occuried. Try again later")
        else:
            return None

application = webapp2.WSGIApplication([
    (r"%s"%(PROJECT_ACTION_URL), api_project_action),
    (r"%s"%(BRANCH_ACTION_URL), api_branch_action)
], debug=True)
