#!/usr/bin/env python

import json, src.octo.utils as utils

# Spark job to consolidate all the settings to launch spark-submit script
class SparkJob(object):
    def __init__(self, uid, name, entrypoint, jar, options, jobconf=[]):
        self.uid = uid
        self.name = name
        self.entrypoint = utils.validateEntrypoint(entrypoint)
        self.jar = utils.validateJarPath(jar)
        self.options = {}
        # perform options check
        for (key, value) in options.items():
            if key == "spark.driver.memory" or key == "spark.executor.memory":
                self.options[key] = utils.validateMemory(value)
            else:
                self.options[key] = value
        # jobconf is a job configuration relevant to the jar running, or parameters for the main
        # class of the jar
        self.jobconf = jobconf

    # returns shell command to execute as a list of arguments
    # - master => Spark Master URL, or "local[*]" for running in local mode
    # - additionalOptions => extra options to add to the execute command. They are transient and
    # therefor will not be saved as job options.
    def execCommand(self, master, additionalOptions={}):
        # spark-submit --master sparkurl --conf "" --conf "" --class entrypoint jar
        sparkSubmit = ["spark-submit"]
        name = ["--name", "%s" % self.name]
        master = ["--master", "%s" % master]
        # update options with `additionalOptions` argument
        confOptions = self.options.copy()
        confOptions.update(additionalOptions)
        # create list of conf options, ready to be used in cmd, flatten conf
        conf = [["--conf", "%s=%s" % (key, value)] for key, value in confOptions.items()]
        conf = [num for elem in conf for num in elem]
        entrypoint = ["--class", "%s" % self.entrypoint]
        jar = ["%s" % self.jar]
        # jobconf
        jobconf = ["%s" % elem for elem in self.jobconf]
        # construct exec command for shell
        cmd = sparkSubmit + name + master + conf + entrypoint + jar + jobconf
        return cmd

    def json(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "entrypoint": self.entrypoint,
            "jar": self.jar,
            "options": self.options,
            "jobconf": self.jobconf
        }

    def dict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "entrypoint": self.entrypoint,
            "jar": self.jar,
            "options": json.dumps(self.options),
            "jobconf": json.dumps(self.jobconf)
        }

    @classmethod
    def fromDict(cls, obj):
        # validate spark job uid to fetch only SparkJob instances
        uid = obj["uid"]
        name = obj["name"]
        entrypoint = obj["entrypoint"]
        jar = obj["jar"]
        options = utils.jsonOrElse(obj["options"], None)
        jobconf = utils.jsonOrElse(obj["jobconf"], None)
        if options is None:
            raise StandardError("Could not process options: %s" % obj["options"])
        if jobconf is None:
            raise StandardError("Could not process job configuration: %s" % obj["jobconf"])
        return cls(uid, name, entrypoint, jar, options, jobconf)
