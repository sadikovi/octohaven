#!/usr/bin/env python

import urllib2
import json
from job import JobCheck

SPARK_REST_ENDPOINT = "/api/v1"
SPARK_REST_APPLICATIONS = "/applications"

# Spark cluster statuses
FREE = 0
BUSY = -1
DOWN = -2

class SparkModule(object):
    def __init__(self, masterAddress, uiAddress, uiRunAddress):
        # master address to launch applications using "spark-submit"
        self.masterAddress = JobCheck.validateMasterUrl(masterAddress)
        # address for Spark UI
        self.uiAddress = JobCheck.validateUiUrl(uiAddress)
        # address for a running application in Spark
        self.uiRunAddress = JobCheck.validateUiUrl(uiRunAddress)

    # returns current Spark cluster status
    def clusterStatus(self):
        status = FREE
        arr = list()
        try:
            f = urllib2.urlopen(self.uiAddress + SPARK_REST_ENDPOINT + SPARK_REST_APPLICATIONS)
            arr = json.loads(f.read())
            index, ln = 0, len(arr)
            while index < ln and status == FREE:
                attempts = arr[index][u'attempts']
                for attempt in attempts:
                    completed = attempt[u'completed']
                    if not completed:
                        status = BUSY
                        break
                index += 1
        except:
            status = DOWN
        # return final status, if nothing has changed, then status will be "okay"
        return status
