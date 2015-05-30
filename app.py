#!/usr/bin/env python

# import libs
import _paths
from google.appengine.api import users
from google.appengine.ext.webapp import template
import webapp2
import os
import re
import urllib2
import src.redis.config as config
from src.connector.redisconnector import RedisConnectionPool, RedisConnector
from src.redis.manager import Manager
from src.redis.core import Project, Branch
from src.redis.errors import CoreError

# init pool
octohaven_pool = RedisConnectionPool(config.settings)

# constants
START_PAGE = "welcome.html"
HOME_PAGE = "home.html"
UNAVAILABLE_PAGE = "unavailable.html"
NOTFOUND_PAGE = "notfound.html"
PROJECT_NEW_PAGE = "newproject.html"
PROJECT_PAGE = "project.html"
EDITOR_PAGE = "editor.html"
# cookies
TIMEZONE_COOKIE = "octohaven_timezone_cookie"

def fullpath():
    return os.path.join(os.path.dirname(__file__), "static")

def tzoffset(value):
    try:
        return int(value)
    except:
        return None

def manager():
    rc = RedisConnector(poolhandler=octohaven_pool)
    return Manager(connector=rc)

def _template():
    return {
        "values": {
            "home_url": "/",
            "login_url": "/auth/login",
            "logout_url": "/auth/logout",
            "userdash_url": "/user"
        },
        "file": START_PAGE
    }

class app_home(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        offset = tzoffset(self.request.cookies.get(TIMEZONE_COOKIE))
        web_template = _template()
        if user:
            try:
                mngr, puserid = manager(), user.user_id()
                puser, projects = mngr.getUser(puserid), None
                if puser:
                    projectgroup = mngr.getProjectGroup(puser.hash())
                    projects = projectgroup.projects()
                else:
                    mngr.createUser(puserid, user.nickname(), user.email())
            except:
                web_template["file"] = UNAVAILABLE_PAGE
            else:
                # list of objects with local time
                lprojects = []
                if projects:
                    projects = sorted(projects, cmp=lambda x, y: cmp(x._created, y._created), reverse=True)
                    lprojects = [{"name": x.name(), "desc": x.desc(), "datetime": x.datetime(offset=offset)} for x in projects]
                # prepare template values
                web_template["values"]["username"] = user.nickname()
                web_template["values"]["create_url"] = "/project/new"
                web_template["values"]["project_url"] = "/project/"
                web_template["values"]["projects"] = lprojects
                web_template["file"] = HOME_PAGE
        # load template
        path = os.path.join(fullpath(), web_template["file"])
        self.response.out.write(template.render(path, web_template["values"]))

class app_redirect(webapp2.RequestHandler):
    def get(self):
        self.redirect("/")

class app_notfound(webapp2.RequestHandler):
    def get(self):
        web_template = _template()
        web_template["file"] = NOTFOUND_PAGE
        path = os.path.join(fullpath(), web_template["file"])
        self.response.out.write(template.render(path, web_template["values"]))

class app_project_new(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        web_template = _template()
        if user:
            web_template["values"]["username"] = user.nickname()
            web_template["file"] = PROJECT_NEW_PAGE
        # load template
        path = os.path.join(fullpath(), web_template["file"])
        self.response.out.write(template.render(path, web_template["values"]))

class app_project(webapp2.RequestHandler):
    def get(self, *args):
        user = users.get_current_user()
        web_template = _template()
        if user:
            try:
                mngr = manager()
                puser = mngr.getUser(user.user_id())
                if not puser:
                    raise CoreError("Requested user does not exist. Please re-login")
                pname = "%s"%(args[0]) if args else None
                pname = Project.validateName(pname)
                projectgroup = mngr.getProjectGroup(puser.hash())
                project = projectgroup.project(pname)
                if project:
                    web_template["values"]["username"] = user.nickname()
                    web_template["values"]["project"] = project
                    web_template["file"] = PROJECT_PAGE
                else:
                    raise CoreError("Project {%s} is not recognized"%(pname))
            except CoreError as ce:
                web_template["file"] = NOTFOUND_PAGE
            except:
                web_template["file"] = UNAVAILABLE_PAGE
        # load template
        path = os.path.join(fullpath(), web_template["file"])
        self.response.out.write(template.render(path, web_template["values"]))

class app_editor(webapp2.RequestHandler):
    def get(self, *args):
        user = users.get_current_user()
        web_template = _template()
        if user:
            try:
                mngr = manager()
                puser = mngr.getUser(user.user_id())
                if not puser:
                    raise CoreError("Requested user does not exist. Please re-login")
                pname, bname = args if args and len(args) == 2 else (None, None)
                pname = Project.validateName(pname)
                projectgroup = mngr.getProjectGroup(puser.hash())
                project = projectgroup.project(pname)
                if not project:
                    raise CoreError("Project {%s} is not recognized"%(pname))
                bname = Branch.validateName(bname)
                branchgroup = mngr.getBranchGroup(puser.hash(), project.hash())
                branch = branchgroup.branch(bname)
                if not branch:
                    raise CoreError("Branch {%s} is not recognized"%(bname))
                # branch and project are valid
                web_template["values"]["username"] = user.nickname()
                web_template["values"]["project_url"] = "/project/%s"%(project.name())
                web_template["values"]["project"] = project
                web_template["values"]["branch"] = branch
                web_template["file"] = EDITOR_PAGE
            except CoreError as ce:
                web_template["file"] = NOTFOUND_PAGE
            except:
                web_template["file"] = UNAVAILABLE_PAGE
        # load template
        path = os.path.join(fullpath(), web_template["file"])
        self.response.out.write(template.render(path, web_template["values"]))

application = webapp2.WSGIApplication([
    ("/", app_home),
    ("/project/new", app_project_new),
    (r"/project/([^/]*)", app_project),
    (r"/project/([^/]*)/branch/([^/]*)", app_editor),
    ("/home|/index|/index\.html", app_redirect),
    ("/.*", app_notfound)
], debug=True)
