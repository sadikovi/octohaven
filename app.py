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
from src.redis.core import Project

# init pool
octohaven_pool = RedisConnectionPool(config.settings)

# constants
START_PAGE = "welcome.html"
HOME_PAGE = "home.html"
UNAVAILABLE_PAGE = "unavailable.html"
NOTFOUND_PAGE = "notfound.html"
PROJECT_NEW_PAGE = "project_new.html"
PROJECT_PAGE = "project.html"
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

def verifyProjectPath(path):
    regex = "^(/project/)(%s)$"%(Project.ID_REGEXP(closed=False))
    parts = re.match(regex, path, re.I)
    return urllib2.unquote(parts.groups()[1]) if parts and len(parts.groups()) >= 2 else None

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
        # timezone offset
        offset = tzoffset(self.request.cookies.get(TIMEZONE_COOKIE))
        # template file and template values
        web_template = _template()
        if user:
            try:
                # get user
                mngr, puserid = manager(), user.user_id()
                puser, projects = mngr.getUser(puserid), None
                if puser:
                    projects = mngr.projectsForUser(puser.hash(), asobject=True)
                else:
                    mngr.createUser(puserid, user.nickname(), user.email())
            except:
                web_template["file"] = UNAVAILABLE_PAGE
            else:
                # list of objects with local time
                lprojects = []
                if projects:
                    projects = sorted(projects, cmp=lambda x, y: cmp(x._created, y._created), reverse=True)
                    lprojects = [{"id": x.id(), "name": x.name(), "datetime": x.datetime(offset=offset)} for x in projects]
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
    def get(self):
        user = users.get_current_user()
        if user:
            projectid = verifyProjectPath(self.request.path)
            web_template = _template()
            try:
                mngr = manager()
                puser = mngr.getUser(user.user_id())
                if not puser:
                    raise CoreError("Requested user does not exist. Please re-login")
                project = manager().getProject(puser.hash(), projectid)
                if project:
                    web_template["values"]["username"] = user.nickname()
                    web_template["values"]["project"] = project
                    web_template["file"] = PROJECT_PAGE
                else:
                    web_template["file"] = NOTFOUND_PAGE
            except:
                # log error
                web_template["file"] = UNAVAILABLE_PAGE
        # load template
        path = os.path.join(fullpath(), web_template["file"])
        self.response.out.write(template.render(path, web_template["values"]))

application = webapp2.WSGIApplication([
    ("/", app_home),
    ("/project/new", app_project_new),
    ("/project/.*", app_project),
    ("/home|/index|/index\.html", app_redirect),
    ("/.*", app_notfound)
], debug=True)
