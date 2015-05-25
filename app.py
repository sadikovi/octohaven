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

# init pool
octohaven_pool = RedisConnectionPool(config.settings)

# constants
START_PAGE = "start.html"
HOME_PAGE = "home.html"
UNAVAILABLE_PAGE = "unavailable.html"

def fullpath():
    return os.path.join(os.path.dirname(__file__), "static")

class Home(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template_file, template_values = START_PAGE,  {}
        if not user:
            template_file = START_PAGE
            template_values = { "login_url": "/auth/login" }
        else:
            # check if user exists or not
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
            print projects
            # if exists - fetch projects
            template_values = { "username": user.nickname(), "logout_url": "/auth/logout" }
            template_file = HOME_PAGE
        # load template
        path = os.path.join(fullpath(), template_file)
        self.response.out.write(template.render(path, template_values))

class Redirect(webapp2.RequestHandler):
    def get(self):
        self.redirect("/")

application = webapp2.WSGIApplication([
    ("/", Home),
    ("/home|/index|/index\.html", Redirect)
], debug=True)
