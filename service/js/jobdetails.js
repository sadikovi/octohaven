(function() {
  var column, contentHeader, contentList, contentValue, jobDetailsElem, jobid, params, property, row, updateLogLinks, updateScheduleLink, view, _jobapi, _mapper, _misc, _util,
    __slice = [].slice;

  jobDetailsElem = document.getElementById("octohaven-job-details");

  if (!jobDetailsElem) {
    throw new Error("Job details element is not found");
  }

  _mapper = this.mapper;

  _util = this.util;

  _misc = this.misc;

  _jobapi = new this.JobApi;

  contentHeader = function(value) {
    return {
      type: "span",
      cls: "text-mute",
      title: "" + value
    };
  };

  contentValue = function(value) {
    return {
      type: "span",
      title: "" + value
    };
  };

  contentList = function(list) {
    var x, _i, _len, _results;
    _results = [];
    for (_i = 0, _len = list.length; _i < _len; _i++) {
      x = list[_i];
      _results.push({
        type: "p",
        children: {
          type: "span",
          title: "" + x
        }
      });
    }
    return _results;
  };

  column = function(content, islarge) {
    var col, updatedClass;
    if (islarge == null) {
      islarge = false;
    }
    updatedClass = islarge ? "four-fifths column" : "one-fifth column";
    col = {
      type: "div",
      cls: "" + updatedClass,
      children: content
    };
    return _mapper.parseMapForParent(col);
  };

  property = function() {
    var cols, prop, x;
    cols = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
    prop = {
      type: "div",
      cls: "columns",
      children: [
        (function() {
          var _i, _len, _results;
          _results = [];
          for (_i = 0, _len = cols.length; _i < _len; _i++) {
            x = cols[_i];
            _results.push(x);
          }
          return _results;
        })()
      ]
    };
    return _mapper.parseMapForParent(prop);
  };

  row = function(property) {
    var rw;
    rw = {
      type: "div",
      cls: "segment",
      children: property
    };
    return _mapper.parseMapForParent(rw);
  };

  updateLogLinks = function(uid) {
    var stderr, stdout;
    stdout = document.getElementById("octohaven-job-stdout");
    stderr = document.getElementById("octohaven-job-stderr");
    if (stdout) {
      stdout.href = "/log?type=stdout&jobid=" + uid;
    }
    if (stderr) {
      return stderr.href = "/log?type=stderr&jobid=" + uid;
    }
  };

  updateScheduleLink = function(uid) {
    var timetable;
    timetable = document.getElementById("octohaven-job-timetable");
    if (timetable) {
      return timetable.href = "/timetablecreate?id=" + uid + "&mode=create";
    }
  };

  params = _util.windowParameters();

  if ("jobid" in params) {
    jobid = params["jobid"];
    _jobapi.getJob(jobid, function() {
      return jobDetailsElem.innerHTML = "";
    }, function(ok, json) {
      var create, entrypoint, jar, job, jobconf, masterurl, msg, name, options, rowsElem, sparkAppId, status, submit, uid, view, x, y;
      if (ok) {
        job = json["content"]["job"];
        uid = job["uid"];
        name = job["sparkjob"]["name"];
        status = job["status"];
        entrypoint = job["sparkjob"]["entrypoint"];
        masterurl = job["sparkjob"]["masterurl"];
        options = (function() {
          var _ref, _results;
          _ref = job["sparkjob"]["options"];
          _results = [];
          for (x in _ref) {
            y = _ref[x];
            _results.push(x + " = " + y);
          }
          return _results;
        })();
        jobconf = (function() {
          var _i, _len, _ref, _results;
          _ref = job["sparkjob"]["jobconf"];
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            x = _ref[_i];
            _results.push("" + x);
          }
          return _results;
        })();
        jar = job["sparkjob"]["jar"];
        create = job["createtime"];
        submit = job["submittime"];
        sparkAppId = job["sparkappid"] ? job["sparkappid"] : "None";
        rowsElem = {
          type: "div",
          cls: "segments",
          children: [
            row(property(column(contentHeader("Job id"), false), column(contentValue(uid), true))), row(property(column(contentHeader("Spark job name"), false), column(contentValue(name), true))), row(property(column(contentHeader("Created"), false), column({
              type: "span",
              title: "" + (_util.timestampToDate(create))
            }, true))), row(property(column(contentHeader("Expected run"), false), column({
              type: "span",
              title: "" + (_util.timestampToDate(submit))
            }, true))), row(property(column(contentHeader("Status"), false), column(contentValue(status), true))), row(property(column(contentHeader("Entrypoint"), false), column(contentValue(entrypoint), true))), row(property(column(contentHeader("Spark URL"), false), column(contentValue(masterurl), true))), row(property(column(contentHeader("Spark App Id"), false), column(contentValue(sparkAppId), true))), row(property(column(contentHeader("Jar file"), false), column(contentValue(jar), true))), row(property(column(contentHeader("Options"), false), column(contentList(options), true))), row(property(column(contentHeader("Job conf"), false), column(contentList(jobconf), true)))
          ]
        };
        _mapper.parseMapForParent(rowsElem, jobDetailsElem);
        updateLogLinks(uid);
        return updateScheduleLink(uid);
      } else {
        msg = json ? json["content"]["msg"] : "We know and keep working on that";
        view = _misc.blankslateWithMsg("Something went wrong", msg);
        return _mapper.parseMapForParent(view, jobDetailsElem);
      }
    });
  } else {
    jobDetailsElem.innerHTML = "";
    view = _misc.blankslateWithMsg("Something went wrong", "We know and keep working on that");
    _mapper.parseMapForParent(view, jobDetailsElem);
  }

}).call(this);
