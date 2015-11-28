// Generated by CoffeeScript 1.9.0
(function() {
  var Filelist, JobLoader, JobResolver, LogReader, Status, TemplateLoader, TimetableLoader, loader, util;

  loader = this.loader;

  util = this.util;

  Status = (function() {
    Status.STATUS_PENDING = "Pending...";

    Status.STATUS_READY = "Server is ready";

    Status.STATUS_BUSY = "Server is busy";

    Status.STATUS_UNREACHABLE = "Server is unreachable";

    function Status() {}

    Status.prototype.requestStatus = function(before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("get", "/api/v1/spark/status", {}, null, (function(_this) {
        return function(code, response) {
          var data, json, masterAddress, status, uiAddress, _ref;
          json = util.jsonOrElse(response);
          if (json) {
            data = json["content"];
            _ref = [data["status"], data["spark-ui-address"], data["spark-master-address"]], status = _ref[0], uiAddress = _ref[1], masterAddress = _ref[2];
            return typeof after === "function" ? after(status, uiAddress, masterAddress) : void 0;
          } else {
            return typeof after === "function" ? after(false, false, false) : void 0;
          }
        };
      })(this), (function(_this) {
        return function(error, response) {
          return typeof after === "function" ? after(false, false, false) : void 0;
        };
      })(this));
    };

    return Status;

  })();

  if (this.Status == null) {
    this.Status = Status;
  }

  Filelist = (function() {
    function Filelist() {}

    Filelist.prototype.sendRequest = function(url, before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("get", url, {}, null, (function(_this) {
        return function(code, response) {
          var json;
          json = util.jsonOrElse(response);
          if (json) {
            return typeof after === "function" ? after(true, json) : void 0;
          } else {
            return typeof after === "function" ? after(false, json) : void 0;
          }
        };
      })(this), (function(_this) {
        return function(error, response) {
          var json;
          json = util.jsonOrElse(response);
          return typeof after === "function" ? after(false, json) : void 0;
        };
      })(this));
    };

    Filelist.prototype.breadcrumbs = function(directory, before, after) {
      return this.sendRequest("/api/v1/file/breadcrumbs?path=" + (util.quote(directory)), before, after);
    };

    Filelist.prototype.files = function(directory, before, after) {
      return this.sendRequest("/api/v1/file/list?path=" + (util.quote(directory)), before, after);
    };

    return Filelist;

  })();

  if (this.Filelist == null) {
    this.Filelist = Filelist;
  }

  JobResolver = (function() {
    function JobResolver() {}

    JobResolver.prototype.submit = function(data, before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("post", "/api/v1/job/submit", {}, data, (function(_this) {
        return function(code, response) {
          var json;
          json = util.jsonOrElse(response);
          if (json) {
            return typeof after === "function" ? after(true, json) : void 0;
          } else {
            return typeof after === "function" ? after(false, json) : void 0;
          }
        };
      })(this), (function(_this) {
        return function(error, response) {
          var json;
          json = util.jsonOrElse(response);
          return typeof after === "function" ? after(false, json) : void 0;
        };
      })(this));
    };

    return JobResolver;

  })();

  if (this.JobResolver == null) {
    this.JobResolver = JobResolver;
  }

  JobLoader = (function() {
    function JobLoader() {}

    JobLoader.prototype.get = function(status, limit, before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("get", "/api/v1/job/list?status=" + status + "&limit=" + limit, {}, null, function(success, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(!!json, json) : void 0;
      }, function(error, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(false, json) : void 0;
      });
    };

    JobLoader.prototype.close = function(jobid, before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("get", "/api/v1/job/close?jobid=" + jobid, {}, null, function(success, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(!!json, json) : void 0;
      }, function(error, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(false, json) : void 0;
      });
    };

    JobLoader.prototype.getJob = function(jobid, before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("get", "/api/v1/job/get?jobid=" + jobid, {}, null, function(success, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(!!json, json) : void 0;
      }, function(error, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(false, json) : void 0;
      });
    };

    return JobLoader;

  })();

  if (this.JobLoader == null) {
    this.JobLoader = JobLoader;
  }

  TemplateLoader = (function() {
    function TemplateLoader() {}

    TemplateLoader.prototype.show = function(before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("get", "/api/v1/template/list", {}, null, function(success, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(!!json, json) : void 0;
      }, function(error, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(false, json) : void 0;
      });
    };

    TemplateLoader.prototype["delete"] = function(tid, before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("get", "/api/v1/template/delete?templateid=" + tid, {}, null, function(success, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(!!json, json) : void 0;
      }, function(error, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(false, json) : void 0;
      });
    };

    TemplateLoader.prototype.create = function(data, before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("post", "/api/v1/template/create", {}, data, function(success, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(!!json, json) : void 0;
      }, function(error, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(false, json) : void 0;
      });
    };

    return TemplateLoader;

  })();

  if (this.TemplateLoader == null) {
    this.TemplateLoader = TemplateLoader;
  }

  LogReader = (function() {
    function LogReader() {}

    LogReader.prototype.readFromStart = function(jobid, type, page, before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("get", "/api/v1/file/log?" + ("jobid=" + (util.quote(jobid)) + "&type=" + (util.quote(type)) + "&page=" + (util.quote(page))), {}, null, function(success, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(!!json, json) : void 0;
      }, function(error, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(false, json) : void 0;
      });
    };

    return LogReader;

  })();

  if (this.LogReader == null) {
    this.LogReader = LogReader;
  }

  TimetableLoader = (function() {
    function TimetableLoader() {}

    TimetableLoader.prototype.submit = function(data, before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("post", "/api/v1/timetable/create", {}, data, (function(_this) {
        return function(code, response) {
          var json;
          json = util.jsonOrElse(response);
          if (json) {
            return typeof after === "function" ? after(true, json) : void 0;
          } else {
            return typeof after === "function" ? after(false, json) : void 0;
          }
        };
      })(this), (function(_this) {
        return function(error, response) {
          var json;
          json = util.jsonOrElse(response);
          return typeof after === "function" ? after(false, json) : void 0;
        };
      })(this));
    };

    TimetableLoader.prototype.list = function(includeJobs, statuses, before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("get", "/api/v1/timetable/list?includejobs=" + (util.quote(includeJobs)) + "&status=" + (util.quote(statuses)), {}, null, function(success, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(!!json, json) : void 0;
      }, function(error, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(false, json) : void 0;
      });
    };

    TimetableLoader.prototype.get = function(id, before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("get", "/api/v1/timetable/get?id=" + (util.quote(id)), {}, null, function(success, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(!!json, json) : void 0;
      }, function(error, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(false, json) : void 0;
      });
    };

    TimetableLoader.prototype.pause = function(id, before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("get", "/api/v1/timetable/pause?id=" + (util.quote(id)), {}, null, function(success, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(!!json, json) : void 0;
      }, function(error, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(false, json) : void 0;
      });
    };

    TimetableLoader.prototype.resume = function(id, before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("get", "/api/v1/timetable/resume?id=" + (util.quote(id)), {}, null, function(success, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(!!json, json) : void 0;
      }, function(error, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(false, json) : void 0;
      });
    };

    TimetableLoader.prototype.cancel = function(id, before, after) {
      if (typeof before === "function") {
        before();
      }
      return loader.sendrequest("get", "/api/v1/timetable/cancel?id=" + (util.quote(id)), {}, null, function(success, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(!!json, json) : void 0;
      }, function(error, response) {
        var json;
        json = util.jsonOrElse(response);
        return typeof after === "function" ? after(false, json) : void 0;
      });
    };

    return TimetableLoader;

  })();

  if (this.TimetableLoader == null) {
    this.TimetableLoader = TimetableLoader;
  }

}).call(this);
