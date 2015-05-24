#!/usr/bin/env python

from src.mysql.metastore import Util
import uuid

# Abstract classes
class Global(object):
    def __init__(self, uniqueid, id, created):
        if not Util.checknumericid(uniqueid):
            raise StandardError(":Global - unique id is incorrect")
        if not Util.checkid(id):
            raise StandardError(":Global - id is incorrect")
        # assign correct values
        self.uniqueid, self.id = uniqueid, id
        self.created = created

class Revision(object):
    def __init__(self, revisionid, created, latest=True):
        if not Util.checknumericid(revisionid):
            raise StandardError(":Revision - revision id is incorrect")
        self.revisionid = revisionid
        self.created = created
        self.latest = bool(latest)

# Applied classes
class User(Global):
    def __init__(self, uniqueid, id, created):
        super(User, self).__init__(uniqueid, id, created)
        self.projects = {}

    def addProject(self, project):
        if type(project) is not Project:
            raise StandardError(":User - required Project, received %s"%(type(project)))
        self.projects[project.uniqueid] = project

class Project(Global):
    def __init__(self, uniqueid, id, created, user):
        if type(user) is not User:
            raise StandardError(":Project - required User, passed %s"%(type(user)))
        super(Project, self).__init__(uniqueid, id, created)
        self.user = user
        self.branches = {}

    def addBranch(self, branch):
        if type(branch) is not Branch:
            raise StandardError(":Project - required Branch, received %s"%(type(branch)))
        self.branches[branch.uniqueid] = branch

class Branch(Global):
    def __init__(self, uniqueid, id, created, project):
        if type(project) is not Project:
            raise StandardError(":Branch - required Project, passed %s"%(type(project)))
        super(Branch, self).__init__(uniqueid, id, created)
        self.project = project
        self.revisions = {}
        self.latestRevision = None

    def addRevision(self, revision):
        if type(revision) is not BranchRevision:
            raise StandardError(":Branch - required BranchRevision, passed %s"%(type(revision)))
        self.revisions[revision.revisionid] = revision
        if revision.latest:
            self.latestRevision = revision

class BranchRevision(Revision):
    def __init__(self, revisionid, created, latest, branch):
        if type(branch) is not Branch:
            raise StandardError(":BranchRevision - required Branch, passed %s"%(type(branch)))
        super(BranchRevision, self).__init__(revisionid, created, latest)
        self.branch = branch
        self.modules = {}

    def addModule(self, abs_order, module):
        if type(module) is not Module:
            raise StandardError(":BranchRevision - required Module, passed %s"%(type(module)))
        if abs_order in self.modules:
            raise StandardError(":BranchRevision - ordering is broken")
        self.modules[abs_order] = module

# Module does not have latest revision, because it can be reused in any branch,
# and for each branch it will be latest
class Module(Global):
    def __init__(self, uniqueid, created):
        super(Module, self).__init__(
            uniqueid, uuid.uuid3(uuid.NAMESPACE_DNS, str(uniqueid)).hex, created
        )
        self.revisions = {}

    def addRevision(self, revision):
        if type(revision) is not ModuleRevision:
            raise StandardError(":Module - required ModuleRevision, passed %s"%(type(revision)))
        self.revisions[revision.revisionid] = revision

class ModuleRevision(Revision):
    def __init__(self, revisionid, created, latest, module, content):
        if type(module) is not Module:
            raise StandardError(":ModuleRevision - required Module, passed %s"%(type(module)))
        super(ModuleRevision, self).__init__(revisionid, created, latest)
        self.module = module
        self.content = content

class Component(Global):
    def __init__(self, uniqueid, userid, id, type, fileurl, created):
        super(Component, self).__init__(self, uniqueid, id, created)
        self.type = type
        self.fileurl = fileurl
        self.revisions = {}

    def addRevision(self, revision):
        if type(revision) is not ComponentRevision:
            raise StandardError(":Component - required ComponentRevision, passed %s"%(type(revision)))
        self.revisions[revision.uniqueid] = revision

class ComponentRevision(Revision):
    def __init__(self, revisionid, created, latest, component):
        if type(component) is not Component:
            raise StandardError(":ComponentRevision - required Component, passed %s"%(type(component)))
        super(ComponentRevision, self).__init__(revisionid, created, latest)
        self.component = component
