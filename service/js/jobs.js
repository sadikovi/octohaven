(function() {
  var ALL, CLOSED, CREATED, DELAYED, FINISHED, RUNNING, WAITING, actionLabel, all, buttonColumn, closed, created, delayed, finished, jobColumn, jobHistory, reloadJobs, resetLabels, row, running, selectLabel, statusColour, statusColumn, waiting, _jobapi, _loader, _mapper, _misc, _ref, _util;

  jobHistory = document.getElementById("octohaven-jobs-history");

  if (!jobHistory) {
    throw new Error("Job history element could not be found");
  }

  _util = this.util;

  _mapper = this.mapper;

  _loader = this.loader;

  _misc = this.misc;

  _jobapi = new this.JobApi;

  _ref = ["ALL", "CREATED", "FINISHED", "WAITING", "CLOSED", "DELAYED", "RUNNING"], ALL = _ref[0], CREATED = _ref[1], FINISHED = _ref[2], WAITING = _ref[3], CLOSED = _ref[4], DELAYED = _ref[5], RUNNING = _ref[6];

  statusColumn = function(status, colour, islarge) {
    var elem, statusElem, statusSection, statusText, updatedClass;
    if (islarge == null) {
      islarge = false;
    }
    updatedClass = islarge ? "one-third column" : "one-sixth column";
    statusText = {
      type: "span",
      cls: "" + colour,
      title: "" + status
    };
    statusSection = {
      type: "div",
      cls: "section",
      children: statusText
    };
    statusElem = {
      type: "div",
      cls: "breadcrumb",
      children: statusSection
    };
    elem = {
      type: "div",
      cls: "" + updatedClass,
      children: statusElem
    };
    return _mapper.parseMapForParent(elem);
  };

  buttonColumn = function(btnTitle, action, islarge) {
    var btn, elem, updatedClass;
    if (islarge == null) {
      islarge = false;
    }
    updatedClass = islarge ? "one-third column" : "one-sixth column";
    btn = {
      type: "div",
      cls: "btn btn-compact",
      title: "" + btnTitle,
      onclick: function(e) {
        return typeof action === "function" ? action(this) : void 0;
      }
    };
    elem = {
      type: "div",
      cls: "" + updatedClass,
      children: btn
    };
    return _mapper.parseMapForParent(elem);
  };

  jobColumn = function(name, link, prefix, timestamp) {
    var column, datetime, elem, job, jobLink, jobSection, jobSuffix, timePrefix, timeSection;
    column = "two-thirds column";
    jobLink = {
      type: "a",
      href: "" + link,
      title: "" + name
    };
    jobSuffix = {
      type: "span",
      cls: "text-mute",
      title: "@Spark"
    };
    jobSection = {
      type: "div",
      cls: "section",
      children: [jobLink, jobSuffix]
    };
    timePrefix = {
      type: "span",
      cls: "text-mute",
      title: "" + prefix
    };
    datetime = {
      type: "span",
      title: "" + (_util.humanReadableTime(timestamp))
    };
    timeSection = {
      type: "div",
      cls: "section",
      children: [timePrefix, datetime]
    };
    job = {
      type: "div",
      cls: "breadcrumb",
      children: [jobSection, timeSection]
    };
    elem = {
      type: "div",
      cls: "" + column,
      children: job
    };
    return _mapper.parseMapForParent(elem);
  };

  statusColour = function(status) {
    if (status === CREATED) {
      return "text-green";
    }
    if (status === WAITING) {
      return "text-yellow";
    }
    if (status === RUNNING) {
      return "text-teal";
    }
    if (status === FINISHED) {
      return "text-blue";
    }
    if (status === CLOSED) {
      return "text-red";
    }
    return "text-mute";
  };

  row = function(jobObj) {
    var buttonCol, columns, jobCol, name, segment, showClose, status, statusCol, submittime, uid;
    uid = jobObj["uid"];
    submittime = jobObj["createtime"];
    status = jobObj["status"];
    name = jobObj["sparkjob"]["name"];
    jobCol = jobColumn(name, "/job?jobid=" + uid, "Created ", submittime);
    showClose = status === CREATED || status === DELAYED || status === WAITING;
    statusCol = statusColumn(status, statusColour(status), !showClose);
    buttonCol = buttonColumn("Close", function(e) {
      var fetch, update;
      if (e.uid == null) {
        e.uid = uid;
      }
      fetch = (function(_this) {
        return function() {
          _util.addClass(e, "btn-disabled");
          return e.innerHTML = "???";
        };
      })(this);
      update = (function(_this) {
        return function(ok) {
          _util.addClass(e, "btn-disabled");
          return e.innerHTML = ok ? "Closed" : "Error";
        };
      })(this);
      return _jobapi.close(e.uid, (function() {
        return fetch();
      }), (function(ok, json) {
        return update(ok);
      }));
    });
    columns = {
      type: "div",
      cls: "columns",
      children: [jobCol, statusCol, showClose ? buttonCol : null]
    };
    segment = {
      type: "div",
      cls: "segment",
      children: columns
    };
    return _mapper.parseMapForParent(segment);
  };

  reloadJobs = function(status, limit) {
    if (limit == null) {
      limit = 30;
    }
    return _jobapi.get(status, limit, function() {
      return jobHistory.innerHTML = "";
    }, function(ok, json) {
      var header, job, jobs, link, msg, rows, segment, text;
      if (ok && json) {
        jobs = json["content"]["jobs"];
        if (jobs.length > 0) {
          rows = [
            (function() {
              var _i, _len, _results;
              _results = [];
              for (_i = 0, _len = jobs.length; _i < _len; _i++) {
                job = jobs[_i];
                _results.push(row(job));
              }
              return _results;
            })()
          ];
          segment = {
            type: "div",
            cls: "segments",
            children: rows
          };
          return _mapper.parseMapForParent(segment, jobHistory);
        } else {
          header = {
            type: "h1",
            cls: "text-thin",
            title: "No jobs found :("
          };
          link = {
            type: "a",
            href: "/create",
            title: "create a new job"
          };
          text = {
            type: "p",
            title: "You can ",
            children: link
          };
          return _mapper.parseMapForParent(_misc.blankslate([header, text]), jobHistory);
        }
      } else {
        msg = json ? "" + json["content"]["msg"] : "We do not know what happened :(";
        header = "Something went wrong";
        return _mapper.parseMapForParent(_misc.blankslateWithMsg(header, msg), jobHistory);
      }
    });
  };

  all = document.getElementById("octohaven-jobs-all");

  created = document.getElementById("octohaven-jobs-created");

  waiting = document.getElementById("octohaven-jobs-waiting");

  delayed = document.getElementById("octohaven-jobs-delayed");

  running = document.getElementById("octohaven-jobs-running");

  finished = document.getElementById("octohaven-jobs-finished");

  closed = document.getElementById("octohaven-jobs-closed");

  resetLabels = function() {
    _util.removeClass(all, "selected");
    _util.removeClass(created, "selected");
    _util.removeClass(waiting, "selected");
    _util.removeClass(delayed, "selected");
    _util.removeClass(running, "selected");
    _util.removeClass(finished, "selected");
    return _util.removeClass(closed, "selected");
  };

  selectLabel = function(elem) {
    return _util.addClass(elem, "selected");
  };

  actionLabel = function(e, elem, label) {
    resetLabels();
    selectLabel(elem);
    if (typeof reloadJobs === "function") {
      reloadJobs(label);
    }
    if (e != null) {
      e.preventDefault();
    }
    return e != null ? e.stopPropagation() : void 0;
  };

  _util.addEventListener(all, "click", function(e) {
    return actionLabel(e, all, ALL);
  });

  _util.addEventListener(created, "click", function(e) {
    return actionLabel(e, created, CREATED);
  });

  _util.addEventListener(waiting, "click", function(e) {
    return actionLabel(e, waiting, WAITING);
  });

  _util.addEventListener(delayed, "click", function(e) {
    return actionLabel(e, delayed, DELAYED);
  });

  _util.addEventListener(running, "click", function(e) {
    return actionLabel(e, running, RUNNING);
  });

  _util.addEventListener(finished, "click", function(e) {
    return actionLabel(e, finished, FINISHED);
  });

  _util.addEventListener(closed, "click", function(e) {
    return actionLabel(e, closed, CLOSED);
  });

  actionLabel(null, all, ALL);

}).call(this);
