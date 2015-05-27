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
from src.redis.errors import CoreError
import src.redis.config as config
from src.redis.manager import Manager
from src.connector.redisconnector import RedisConnectionPool, RedisConnector

# init pool
octohaven_pool = RedisConnectionPool(config.settings)

def manager(userid=None):
    # check if user exists or not
    rc = RedisConnector(poolhandler=octohaven_pool)
    manager = Manager(connector=rc)
    if userid and not manager.getUser(userid):
        rc, manager = None, None
        raise CoreError("Requested user does not exist. Please re-login")
    return manager

def validateProjectIdAndName(projectid, projectname, userid, managerfunc):
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
            if not managerfunc:
                pass
            else:
                proj = managerfunc.getProject(userid, projectid)
                if proj:
                    return APIResult(APIResultStatusError400(), "Project {%s} already exists"%(projectid))
    if projectname:
        # validate projectname
        pass
    return result

class api_project_validate(webapp2.RequestHandler):
    def get(self):
        # you can specify id, name
        result = None
        user = users.get_current_user()
        if not user:
            # raise authentication error
            result = APIResult(APIResultStatusError401(), "Not authenticated. Please re-login")
        else:
            try:
                projectid = urllib2.unquote(self.request.get("id")).strip()
                projectname = urllib2.unquote(self.request.get("name").strip())
                puserid = user.user_id()
                result = validateProjectIdAndName(projectid, projectname, puserid, manager(puserid))
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

class api_project_new(webapp2.RequestHandler):
    def post(self):
        user, result = users.get_current_user(), None
        if not user:
            # raise authentication error
            result = APIResult(APIResultStatusError401(), "Not authenticated. Please re-login")
        else:
            data = self.request.body.strip()
            try:
                data = json.loads(data)
            except:
                data = None
            else:
                # unquote values
                for k, v in data.items():
                    k, v = k.strip().lower(), v.strip()
                    data[k] = urllib2.unquote(v)
            pidkey, pnamekey = "projectid", "projectname"
            # perform check
            projectid = data[pidkey] if pidkey in data else ""
            projectname = data[pnamekey] if pnamekey in data else ""
            puserid = user.user_id()
            try:
                mngr = manager(puserid)
                result = validateProjectIdAndName(projectid, projectname, puserid, mngr)
                if result.type() == APIResultStatusSuccess:
                    newproject = mngr.createProject(puserid, projectid, projectname)
                    mngr.addProjectForUser(puserid, newproject.id())
                    # everything is okay
                    data = {
                        "redirect": "/project/%s?isnew=1"%(newproject.id()),
                        "isnew": True
                    }
                    result = APIResult(APIResultStatusSuccess(), "All good", data)
            except CoreError as ce:
                # report error
                result = APIResult(APIResultStatusError400(), ce._msg)
            except KeyError:
                # report general error
                result = APIResult(APIResultStatusError400(), "General error occuried. Try again later")

            # something is wrong with workflow
            if not result:
                result = APIResult(APIResultStatusError500(), "Workflow issues. Try again later")
        # send request
        self.response.headers["Content-Type"] = "application/json"
        self.response.set_status(result.code())
        self.response.out.write(json.dumps(result.dict()))

class api_project_update(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            result = APIResult(APIResultStatusError401(), "Not authenticated. Please re-login")
        else:
            try:
                projectid = urllib2.unquote(self.request.get("id")).strip().lower()
                projectname = urllib2.unquote(self.request.get("name").strip())
                puserid = user.user_id()
                mngr = manager(puserid)
                result = validateProjectIdAndName(projectid, projectname, puserid, None)
                if result.type() == APIResultStatusSuccess:
                    # fetch project
                    proj = mngr.updateProject(puserid, projectid, projectname)
                    if not proj:
                        result = APIResult(APIResultStatusError400(), "Project id does not exist")
                    else:
                        result = APIResult(APIResultStatusSuccess(), "All good", {})
            except CoreError as ce:
                result = APIResult(APIResultStatusError400(), ce._msg)
            except KeyError:
                result = APIResult(APIResultStatusError500(), "Something went wrong. Try again later")
            else:
                if not result:
                    # some workflow issue
                    result = APIResult(APIResultStatusError500(), "Workflow issues. Try again later")
        # send request
        self.response.headers["Content-Type"] = "application/json"
        self.response.set_status(result.code())
        self.response.out.write(json.dumps(result.dict()))

class api_project_delete(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if not user:
            result = APIResult(APIResultStatusError401(), "Not authenticated. Please re-login")
        else:
            try:
                data = self.request.body.strip()
                try:
                    data = json.loads(data)
                except:
                    data = None
                else:
                    # unquote values
                    for k, v in data.items():
                        k, v = k.strip().lower(), v.strip()
                        data[k] = urllib2.unquote(v)
                pidkey = "projectid"
                # perform check
                projectid = data[pidkey] if pidkey in data else ""
                puserid = user.user_id()
                mngr = manager(puserid)
                # delete project
                delproj = mngr.deleteProject(puserid, projectid)
                mngr.removeProjectForUser(puserid, projectid)
                if delproj:
                    # everything is okay
                    data = { "redirect": "/", "isdeleted": True }
                    result = APIResult(APIResultStatusSuccess(), "All good", data)
                else:
                    result = APIResult(APIResultStatusError400(), "Project cannot be deleted", {})
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

application = webapp2.WSGIApplication([
    ("/api/project/validate", api_project_validate),
    ("/api/project/update", api_project_update),
    ("/api/project/delete", api_project_delete),
    ("/api/project/new", api_project_new)
], debug=True)
