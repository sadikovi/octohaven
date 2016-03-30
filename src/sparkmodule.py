#!/usr/bin/env python

#
# Copyright 2015 sadikovi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import urllib2, json, re, utils
from types import ListType
from webparser import Parser
from loggable import Loggable

SPARK_REST_ENDPOINT = "/api/v1"
SPARK_REST_APPLICATIONS = "/applications"
SPARK_RES_ENVIRONMENT = "/environment"
# Job id in Spark UI that is assigned by Spark
SPARK_APP_ID = "spark.app.id"
# Job id assigned by Octohaven
SPARK_OCTOHAVEN_JOB_ID = "spark.octohaven.jobId"

# Spark cluster statuses
FREE = 0
BUSY = -1
DOWN = -2

class SparkContext(Loggable, object):
    def __init__(self, masterAddress, uiAddress, uiRunAddress):
        super(SparkContext, self).__init__()
        # master address to launch applications using "spark-submit"
        self.masterAddress = utils.validateMasterUrl(masterAddress)
        # address for Spark UI
        self.uiAddress = utils.validateUiUrl(uiAddress)
        # address for a running application in Spark
        data = utils.validateUiUrl(uiRunAddress, as_uri_parts=True)
        self.uiRunAddress, self.uiRunHost, self.uiRunPort = data
        self.logger.debug("Created Spark context with master '%s', UI '%s'",
            masterAddress, uiAddress)

    # Return current active master address
    def getMasterAddress(self):
        return self.masterAddress

    def clusterInfo(self):
        # Returns applications info from Spark.
        # Example of response that we get with /api/v1/applications
        # [ {
        #   "id" : "app-20151022214639-0000",
        #   "name" : "Spark shell",
        #   "attempts" : [ {
        #       "startTime" : "2015-10-22T08:46:39.261GMT",
        #       "endTime" : "1969-12-31T23:59:59.999GMT",
        #       "sparkUser" : "sadikovi",
        #       "completed" : false
        #   } ]
        # } ]
        # if returned object is None, it means that we failed to get a response, and cluster most
        # likely is down. If it is empy, then cluster is free, and nothing is running, otherwise we
        # know appid that is running currently.
        try:
            f = urllib2.urlopen(self.uiAddress + SPARK_REST_ENDPOINT + SPARK_REST_APPLICATIONS)
        except:
            return None
        else:
            # when requested, Spark returns list of jobs
            arr = utils.jsonOrElse(f.read(), None)
            apps = []
            for app in arr:
                if "id" in app and "name" in app and "attempts" in app:
                    appid = app["id"]
                    name = app["name"]
                    completed = True
                    for attempt in app["attempts"]:
                        completed = completed and attempt["completed"]
                    apps.append({"id": appid, "name": name, "completed": completed})
            return apps

    # returns list of running apps on Spark cluster
    def clusterRunningApps(self):
        info = self.clusterInfo()
        if type(info) is ListType:
            running = [app for app in info if app["completed"] is False]
            return running
        return None

    # Returns current Spark cluster status
    def clusterStatus(self):
        info = self.clusterInfo()
        if type(info) is ListType:
            running = [app for app in info if app["completed"] is False]
            return FREE if len(running) == 0 else BUSY
        self.logger.warning("Spark cluster is not running - %s", str(info))
        return DOWN

    # Returns list of current apps running, each element of an array is a dictionary:
    # {"sparkid": "app-20151022214639-0000", "jobid": "job_129397ahdf34f342b"}
    def runningApps(self):
        info = self.clusterInfo()
        if not info:
            return None
        running = [app for app in info if app["completed"] is False]
        # for each running application we have to resolve sparkid - jobid pair
        updated = []
        port = self.uiRunPort
        for app in running:
            # ask for running page
            tempUrl = "http://" + self.uiRunHost + ":" + str(port) + SPARK_RES_ENVIRONMENT
            data = self.getWebpageData(tempUrl)
            if data:
                sparkid = self.getValueForKey(self.search(data, SPARK_APP_ID), SPARK_APP_ID)
                jobid = self.getValueForKey(self.search(data, SPARK_OCTOHAVEN_JOB_ID),
                    SPARK_OCTOHAVEN_JOB_ID)
                updated.append({"sparkid": sparkid, "jobid": jobid})
            # increment port for the next application
            port = port + 1
        return updated

    @utils.private
    def search(self, obj, key):
        # search a particular key on a webpage. In this case of Spark UI, we know that options we
        # extract are always in table format.
        # <tr>
        #   <td></td>
        #   <td></td>
        # </tr>
        # validates key to return parent element
        def validateKey(obj, key):
            return True if "data" in obj and obj["data"] == key else False
        if "children" in obj and type(obj["children"]) is ListType:
            for child in obj["children"]:
                if validateKey(child, key):
                    return obj
            allElems = [self.search(each, key) for each in obj["children"]]
            elems = [x for x in allElems if x is not None]
            return elems[0] if len(elems) > 0 else None
        else:
            return None

    @utils.private
    def getWebpageData(self, url):
        # this method is very page specific, do not use it for any other pages different from Spark
        # UI web page for running job.
        try:
            f = urllib2.urlopen(url)
        except:
            return None
        else:
            page = f.read()
            parser = Parser()
            parser.feed(page)
            if len(parser._stack) > 0:
                raise StandardError("HTML content is not properly structured")
            result = {"data": [x.getJSON() for x in parser._root]}
            return result["data"][9]

    @utils.private
    def getValueForKey(self, dom, key):
        # after receiving table row, we know that it has two columns, one of them is key and
        # another is value. We match to the key passed and return value that fails match.
        if not dom or "children" not in dom:
            return None
        for x in dom["children"]:
            value = x["data"] if "data" in x else None
            if value != key:
                return value
        return None
