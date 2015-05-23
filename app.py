#!/usr/bin/env python

# import libs
from google.appengine.api import users
from google.appengine.ext.webapp import template
import webapp2
import json
import os
from types import StringType
import re

class Def(object):
    default_page = "start.html"
    default_values = {}
    directory = "static"

class Home(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template_file, template_values = Def.default_page,  Def.default_values
        if user:
            # create template values
            template_values = {
                "username": user.nickname()
            }
            template_file = "home.html"
        # load template
        path = os.path.join(os.path.dirname(__file__), Def.directory, template_file)
        self.response.out.write(template.render(path, template_values))

class Project(webapp2.RequestHandler):
    def get(self, projectid):
        user = users.get_current_user()
        template_file, template_values = Def.default_page,  Def.default_values
        # validate user and projectid
        if user and type(projectid) is StringType and re.match("^[\w-]+$", projectid, re.I):
            projectid = projectid.lower()
            if projectid == "new":
                # load new project page
                template_file = "project_new.html"
                template_values = {
                    "username": user.nickname()
                }
            else:
                # load specific project page
                template_file = "project_id.html"
        # load template
        path = os.path.join(os.path.dirname(__file__), Def.directory, template_file)
        self.response.out.write(template.render(path, template_values))

class Login(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_login_url("/"))

class Logout(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url("/"))

class Redirect(webapp2.RequestHandler):
    def get(self):
        self.redirect("/")

application = webapp2.WSGIApplication([
    ("/project/(.*)", Project),
    ("/login", Login),
    ("/logout", Logout),
    ("/", Home),
    ("/.*", Redirect)
], debug=True)
