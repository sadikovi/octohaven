#!/usr/bin/env python

# import libs
from google.appengine.api import users
import webapp2
import urllib2
import re
import json
import _paths
from src.redis.core import Project
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

def validateProjectIdAndName(projectid, projectname, hashkey, managerfunc):
    result = APIResult(APIResultStatusSuccess(), "All good")
    if not projectid and not projectname:
        # raise error that nothing was specified
        return APIResult(APIResultStatusError400(), "Parameters are undefined. Please specify parameters")
    if projectid:
        # validate projectid
        if not Project.validateIdLength(projectid):
            return APIResult(APIResultStatusError400(), "Project id must be at least %d characters long"%(Project.MIN_ID_LENGTH()))
        elif not Project.validateIdString(projectid):
            return APIResult(APIResultStatusError400(), "Project id must contain only letters, numbers and dashes")
        else:
            # now check against redis db
            if managerfunc:
                proj = managerfunc.getProject(hashkey, projectid)
                if proj:
                    return APIResult(APIResultStatusError400(), "Project {%s} already exists"%(projectid))
    if projectname:
        # validate projectname
        pass
    return result

# validate project id and name
class api_project_validate(webapp2.RequestHandler):
    def get(self):
        result, user = None, users.get_current_user()
        if not user:
            result = APIResult(APIResultStatusError401(), "Not authenticated. Please re-login")
        else:
            try:
                mngr = manager()
                projectid = urllib2.unquote(self.request.get("id")).strip()
                projectname = urllib2.unquote(self.request.get("name").strip())
                puser = mngr.getUser(user.user_id())
                if not puser:
                    raise CoreError("Requested user does not exist. Please re-login")
                result = validateProjectIdAndName(projectid, projectname, puser._hash, mngr)
            except CoreError as ce:
                result = APIResult(APIResultStatusError400(), ce._msg)
            except:
                result = APIResult(APIResultStatusError500(), "Something went wrong. Try again later")
            else:
                if not result:
                    # some workflow issue
                    result = APIResult(APIResultStatusError500(), "Workflow issues. Try again later")
        # send request
        self.response.headers["Content-Type"] = "application/json"
        self.response.set_status(result.code())
        self.response.out.write(json.dumps(result.dict()))

PROJECT_CREATE = "create"
PROJECT_UPDATE = "update"
PROJECT_DELETE = "delete"
PROJECT_ACTION_URL = "/api/project/(%s|%s|%s)"%(PROJECT_CREATE, PROJECT_UPDATE, PROJECT_DELETE)

def performAction(action, userid, projid, projname):
    if action not in [PROJECT_CREATE, PROJECT_UPDATE, PROJECT_DELETE]:
        return APIResult(APIResultStatusError400(), "Project action is not recognized")
    # else parse data and perform action
    try:
        mngr = manager()
        puser = mngr.getUser(userid)
        if not puser:
            raise CoreError("Requested user does not exist. Please re-login")
        puserhash, result = puser.hash(), None
        if action == PROJECT_CREATE:
            result = validateProjectIdAndName(projid, projname, puserhash, mngr)
            if result.type() == APIResultStatusSuccess:
                newproject = mngr.createProject(puserhash, projid, projname)
                mngr.addProjectForUser(puserhash, newproject.id())
                # everything is okay
                data = {
                    "redirect": "/project/%s?isnew=1"%(newproject.id()),
                    "isnew": True
                }
                result = APIResult(APIResultStatusSuccess(), "All good", data)
        elif action == PROJECT_UPDATE:
            proj = mngr.updateProject(puserhash, projid, projname)
            # raise core error as project does not exist
            if not proj:
                raise CoreError("Project does not exist")
            result = APIResult(APIResultStatusSuccess(), "All good")
        elif action == PROJECT_DELETE:
            mngr.removeProjectForUser(puserhash, projid)
            result = APIResult(APIResultStatusSuccess(), "All good")
        else:
            pass
    except CoreError as ce:
        return APIResult(APIResultStatusError400(), ce._msg)
    except KeyError:
        return APIResult(APIResultStatusError400(), "General error occuried. Try again later")
    else:
        return result

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
            pidkey, pnamekey = "projectid", "projectname"
            # perform check
            projectid = data[pidkey] if pidkey in data else None
            projectname = data[pnamekey] if pnamekey in data else None
            result = performAction(action, user.user_id(), projectid, projectname)
            # something is wrong with workflow
            if not result:
                result = APIResult(APIResultStatusError500(), "Workflow issues. Try again later")
        # send request
        self.response.headers["Content-Type"] = "application/json"
        self.response.set_status(result.code())
        self.response.out.write(json.dumps(result.dict()))

application = webapp2.WSGIApplication([
    ("/api/project/validate", api_project_validate),
    (r"%s"%(PROJECT_ACTION_URL), api_project_action)
], debug=True)
