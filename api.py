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

def validateProjectIdAndName(projectid, projectname):
    result = APIResult(APIResultStatusSuccess(), "All good")
    if not projectid and not projectname:
        # raise error that nothing was specified
        return APIResult(APIResultStatusError400(), "Parameters are undefined. Please specify parameters")
    if projectid:
        # validate projectid
        if not Project.validateIdLength(projectid):
            return APIResult(APIResultStatusError400(), "Project id must be at least 3 characters long")
        elif not Project.validateIdString(projectid):
            return APIResult(APIResultStatusError400(), "Project id must contain only letters, numbers and dashes")
        else:
            pass
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
                projectid = urllib2.unquote(self.request.get("id")).strip().lower()
                projectname = urllib2.unquote(self.request.get("name").strip())
                result = validateProjectIdAndName(projectid, projectname)
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
    ("/api/project/validate", api_project_validate)
], debug=True)
