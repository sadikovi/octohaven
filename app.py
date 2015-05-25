#!/usr/bin/env python

# import libs
import _paths
from google.appengine.api import users
from google.appengine.ext.webapp import template
import webapp2
import os
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
PROJECT_NEW_PAGE = "project_new.html"

def fullpath():
    return os.path.join(os.path.dirname(__file__), "static")

class app_home(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template_file, template_values = START_PAGE,  {}
        if not user:
            template_file = START_PAGE
            template_values = { "login_url": "/auth/login" }
        else:
            # check if user exists or not
            try:
                rc = RedisConnector(poolhandler=octohaven_pool)
                manager = Manager(connector=rc)
                # get user
                octohaven_user, projects = manager.getUser(user.user_id()), None
                if octohaven_user:
                    print "User found!"
                    # get projects
                    projects = manager.projectsForUser(user.user_id(), asobject=True)
                else:
                    # create user
                    manager.createUser(user.user_id(), user.nickname(), user.email())
                    print "User created!"
            except:
                # log error
                # and redirect to the unavailable page
                template_file = UNAVAILABLE_PAGE
                template_values = {}
            else:
                # if exists - fetch projects
                template_values = {
                    "username": user.nickname(),
                    "logout_url": "/auth/logout",
                    "create_url": "/project/new",
                    "projects": projects
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
                "username": user.nickname(),
                "logout_url": "/auth/logout"
            }
            template_file = PROJECT_NEW_PAGE
        # load template
        path = os.path.join(fullpath(), template_file)
        self.response.out.write(template.render(path, template_values))

application = webapp2.WSGIApplication([
    ("/", app_home),
    ("/project/new", app_project_new),
    ("/home|/index|/index\.html", app_redirect)
], debug=True)
