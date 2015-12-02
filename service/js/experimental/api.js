(function() {
  var AbstractApi, FilelistApi, JobApi, LogApi, StatusApi, TemplateApi, TimetableApi, _loader, _util,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
    __hasProp = {}.hasOwnProperty;

  _loader = this.loader;

  _util = this.util;

  AbstractApi = (function() {
    function AbstractApi() {}

    AbstractApi.prototype.doRequest = function(type, before, after, url, data) {
      var atype, k, params, v;
      atype = type.toLowerCase();
      params = {};
      if (data) {
        for (k in data) {
          v = data[k];
          params[_util.quote(k)] = _util.quote(v);
        }
      }
      if (params && atype === "get") {
        url = url + "?" + ((function() {
          var _results;
          _results = [];
          for (k in params) {
            v = params[k];
            _results.push(k + "=" + v);
          }
          return _results;
        })()).join("&");
        params = null;
      }
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest(atype, url, {}, params, function(success, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(!!json, json) : void 0;
      }, function(error, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(false, json) : void 0;
      });
    };

    AbstractApi.prototype.doGet = function(before, after, url, data) {
      if (data == null) {
        data = null;
      }
      return this.doRequest("get", before, after, url, data);
    };

    AbstractApi.prototype.doPost = function(before, after, url, data) {
      return this.doRequest("post", before, after, url, data);
    };

    return AbstractApi;

  })();


  /* API
   */

  StatusApi = (function(_super) {
    __extends(StatusApi, _super);

    function StatusApi() {
      return StatusApi.__super__.constructor.apply(this, arguments);
    }

    StatusApi.prototype.requestStatus = function(before, after) {
      return this.doGet(before, after, "/api/v1/spark/status", null);
    };

    return StatusApi;

  })(AbstractApi);

  if (this.StatusApi == null) {
    this.StatusApi = StatusApi;
  }

  FilelistApi = (function(_super) {
    __extends(FilelistApi, _super);

    function FilelistApi() {
      return FilelistApi.__super__.constructor.apply(this, arguments);
    }

    FilelistApi.prototype.breadcrumbs = function(directory, before, after) {
      return this.doGet(before, after, "/api/v1/file/breadcrumbs", {
        path: "" + directory
      });
    };

    FilelistApi.prototype.files = function(directory, before, after) {
      return this.doGet(before, after, "/api/v1/file/list", {
        path: directory
      });
    };

    return FilelistApi;

  })(AbstractApi);

  if (this.FilelistApi == null) {
    this.FilelistApi = FilelistApi;
  }

  JobApi = (function(_super) {
    __extends(JobApi, _super);

    function JobApi() {
      return JobApi.__super__.constructor.apply(this, arguments);
    }

    JobApi.prototype.get = function(status, limit, before, after) {
      var params;
      params = {
        status: "" + status,
        limit: "" + limit
      };
      return this.doGet(before, after, "/api/v1/job/list", params);
    };

    JobApi.prototype.close = function(id, before, after) {
      return this.doGet(before, after, "/api/v1/job/close", {
        jobid: "" + id
      });
    };

    JobApi.prototype.getJob = function(id, before, after) {
      return this.doGet(before, after, "/api/v1/job/get", {
        jobid: "" + id
      });
    };

    JobApi.prototype.submit = function(data, before, after) {
      return this.doPost(before, after, "/api/v1/job/submit", data);
    };

    return JobApi;

  })(AbstractApi);

  if (this.JobApi == null) {
    this.JobApi = JobApi;
  }

  TemplateApi = (function(_super) {
    __extends(TemplateApi, _super);

    function TemplateApi() {
      return TemplateApi.__super__.constructor.apply(this, arguments);
    }

    TemplateApi.prototype.show = function(before, after) {
      return this.doGet(before, after, "/api/v1/template/list");
    };

    TemplateApi.prototype["delete"] = function(id, before, after) {
      return this.doGet(before, after, "/api/v1/template/delete", {
        templateid: "" + id
      });
    };

    TemplateApi.prototype.create = function(data, before, after) {
      return this.doPost(before, after, "/api/v1/template/create", data);
    };

    return TemplateApi;

  })(AbstractApi);

  if (this.TemplateApi == null) {
    this.TemplateApi = TemplateApi;
  }

  LogApi = (function(_super) {
    __extends(LogApi, _super);

    function LogApi() {
      return LogApi.__super__.constructor.apply(this, arguments);
    }

    LogApi.prototype.readFromStart = function(jobid, type, page, before, after) {
      var params;
      params = {
        jobid: "" + jobid,
        type: "" + type,
        page: "" + page
      };
      return this.doGet(before, after, "/api/v1/file/log", params);
    };

    return LogApi;

  })(AbstractApi);

  if (this.LogApi == null) {
    this.LogApi = LogApi;
  }

  TimetableApi = (function(_super) {
    __extends(TimetableApi, _super);

    function TimetableApi() {
      return TimetableApi.__super__.constructor.apply(this, arguments);
    }

    TimetableApi.prototype.submit = function(data, before, after) {
      return this.doPost(before, after, "/api/v1/timetable/create", data);
    };

    TimetableApi.prototype.list = function(includeJobs, statuses, before, after) {
      var params;
      params = {
        includejobs: "" + includeJobs,
        status: "" + statuses
      };
      return this.doGet(before, after, "/api/v1/timetable/list", params);
    };

    TimetableApi.prototype.get = function(id, before, after) {
      return this.doGet(before, after, "/api/v1/timetable/get", {
        id: "" + id
      });
    };

    TimetableApi.prototype.pause = function(id, before, after) {
      return this.doGet(before, after, "/api/v1/timetable/pause", {
        id: "" + id
      });
    };

    TimetableApi.prototype.resume = function(id, before, after) {
      return this.doGet(before, after, "/api/v1/timetable/resume", {
        id: "" + id
      });
    };

    TimetableApi.prototype.cancel = function(id, before, after) {
      return this.doGet(before, after, "/api/v1/timetable/cancel", {
        id: "" + id
      });
    };

    return TimetableApi;

  })(AbstractApi);

  if (this.TimetableApi == null) {
    this.TimetableApi = TimetableApi;
  }

}).call(this);
