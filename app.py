#!/usr/bin/env python

# import libs
from google.appengine.api import users
from google.appengine.ext.webapp import template
import webapp2
import json
import os
from types import StringType
import re
import urllib2
import json
import _paths
import mysql.connector

a = mysql.connector.connect(
    user="octohaven_user",
    password="octohaven",
    host="localhost",
    port=3306,
    database="octohaven"
)
print a

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

class CreateProject(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if not user:
            result = {"code": 400, "status": "error", "msg": "Authentication required. Please re-login"}
        else:
            projectid = self.request.get("projectid").strip().lower()
            projectname = self.request.get("projectname").strip()
            if not projectid:
                result = {"code": 400, "status": "error", "msg": "Project id is empty. Please send a valid project id"}
            elif len(projectid) < 3:
                result = {"code": 400, "status": "error", "msg": "Project id must be at least 3 characters long"}
            elif not re.match("^[\w-]+$", projectid, re.I):
                result = {"code": 400, "status": "error", "msg": "Project id must only have numbers, letters and dashes"}
            elif False:
                # check on existence
                """ check similar project name in database """
            else:
                # send request to database and create project
                result = {"code": 200, "status": "success", "msg": "Project [ %s ] has been created"%(projectid)}
        self.response.headers['Content-Type'] = "application/json"
        self.response.set_status(result["code"])
        self.response.out.write(json.dumps(result))

class ValidateProject(webapp2.RequestHandler):
    def get(self):
        # send request validate?projectid=
        user = users.get_current_user()
        result = {
            "code": 200,
            "status": "success",
            "message": "All good"
        }

        if not user:
            result["code"] = 401
            result["status"] = "error"
            result["message"] = "Not authenticated. Please re-login"
        else:
            raw = self.request.get("projectid")
            if not raw:
                result["code"] = 400
                result["status"] = "error"
                result["message"] = "Project id is empty. Please send valid project id"
            else:
                projectid = str(urllib2.unquote("%s"%(raw)).strip().lower())
                if len(projectid) < 3:
                    result["code"] = 400
                    result["status"] = "error"
                    result["message"] = "Project id must be at least 3 characters long"
                elif not re.match("^[\w-]+$", projectid, re.I):
                    result["code"] = 400
                    result["status"] = "error"
                    result["message"] = "Project id must only have numbers, letters and dashes"
                else:
                    # check on existence
                    """ check similar project name in database """
        # send request
        self.response.headers['Content-Type'] = "application/json"
        self.response.set_status(result["code"])
        self.response.out.write(json.dumps(result))

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
    ("/project/new/create", CreateProject),
    ("/project/new/validate", ValidateProject),
    ("/project/(.*)", Project),
    ("/login", Login),
    ("/logout", Logout),
    ("/", Home),
    ("/.*", Redirect)
], debug=True)
