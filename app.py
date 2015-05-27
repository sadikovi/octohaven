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

def manager(userid=None):
    # check if user exists or not
    rc = RedisConnector(poolhandler=octohaven_pool)
    manager = Manager(connector=rc)
    if userid and not manager.getUser(userid):
        rc, manager = None, None
        raise CoreError("Requested user does not exist. Please re-login")
    return manager

def verifyProjectPath(path):
    regex = "^(/project/)(%s)$"%(Project.ID_REGEXP(closed=False))
    parts = re.match(regex, path, re.I)
    projectid = urllib2.unquote(parts.groups()[1]) if parts and len(parts.groups()) >= 2 else None
    return projectid

def verifyBranchesPath(path):
    regex = "^(/project/)(%s)(/branches)$"%(Project.ID_REGEXP(closed=False))
    parts = re.match(regex, path, re.I)
    projectid = urllib2.unquote(parts.groups()[1]) if parts and len(parts.groups()) >= 2 else None
    return projectid

class app_home(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        # timezone offset
        offset = tzoffset(self.request.cookies.get(TIMEZONE_COOKIE))
        # template file and template values
        template_file, template_values = START_PAGE,  {}
        if not user:
            template_file = START_PAGE
            template_values = { "login_url": "/auth/login" }
        else:
            # check if user exists or not
            try:
                # get user
                mngr, puserid = manager(), user.user_id()
                octohaven_user, projects = mngr.getUser(puserid), None
                if octohaven_user:
                    # get projects
                    projects = mngr.projectsForUser(puserid, asobject=True, includeNone=False)
                else:
                    # create user
                    mngr.createUser(puserid, user.nickname(), user.email())
            except:
                # log error
                # and redirect to the unavailable page
                template_file = UNAVAILABLE_PAGE
                template_values = {}
            else:
                # list of objects with local time
                lprojects = []
                if projects:
                    projects = sorted(projects, cmp=lambda x, y: cmp(x._created, y._created), reverse=True)
                    for project in projects:
                        lp = {}
                        lp["id"] = project.id()
                        lp["name"] = project.name()
                        lp["datetime"] = project.datetime(offset=offset)
                        lprojects.append(lp)
                # prepare template values
                template_values = {
                    "username": user.nickname(),
                    "home_url": "/",
                    "userdash_url": "/user",
                    "logout_url": "/auth/logout",
                    "create_url": "/project/new",
                    "project_url": "/project/",
                    "projects": lprojects
                }
                template_file = HOME_PAGE
        # load template
        path = os.path.join(fullpath(), template_file)
        self.response.out.write(template.render(path, template_values))

class app_redirect(webapp2.RequestHandler):
    def get(self):
        self.redirect("/")

class app_project_new(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            template_file = START_PAGE
            template_values = { "login_url": "/auth/login" }
        else:
            template_values = {
                "home_url": "/",
                "username": user.nickname(),
                "logout_url": "/auth/logout",
                "userdash_url": "/user",
                "cancel_url": "/"
            }
            template_file = PROJECT_NEW_PAGE
        # load template
        path = os.path.join(fullpath(), template_file)
        self.response.out.write(template.render(path, template_values))



class app_project(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            template_file = START_PAGE
            template_values = { "login_url": "/auth/login" }
        else:
            projectid = verifyProjectPath(self.request.path)
            # fetch project
            puserid = user.user_id()
            try:
                project = manager(puserid).getProject(puserid, projectid)
                if project:
                    template_values = {
                        "home_url": "/",
                        "username": user.nickname(),
                        "projectid": project.id(),
                        "userdash_url": "/user",
                        "logout_url": "/auth/logout",
                        "project": project
                    }
                    template_file = PROJECT_PAGE
                else:
                    template_file = NOTFOUND_PAGE
                    template_values = {}
            except:
                # log error
                template_file = UNAVAILABLE_PAGE
                template_values = {}
        # load template
        path = os.path.join(fullpath(), template_file)
        self.response.out.write(template.render(path, template_values))

application = webapp2.WSGIApplication([
    ("/", app_home),
    ("/project/new", app_project_new),
    ("/project/.*", app_project),
    ("/home|/index|/index\.html", app_redirect)
], debug=True)
