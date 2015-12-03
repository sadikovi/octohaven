(function() {
  var ACTIVE, CANCELLED, PAUSED, actionLabel, actionName, active, cancelled, column, columnAction, columnName, columnStats, columnStatus, noncancelled, paused, resetLabels, row, selectLabel, statusColour, timetablesElem, update, _mapper, _misc, _ref, _timetableApi, _util;

  timetablesElem = document.getElementById("octohaven-timetables");

  if (!timetablesElem) {
    throw new Error("Timetable placeholder is not found");
  }

  _mapper = this.mapper;

  _util = this.util;

  _misc = this.misc;

  _timetableApi = new this.TimetableApi;

  _ref = ["ACTIVE", "PAUSED", "CANCELLED"], ACTIVE = _ref[0], PAUSED = _ref[1], CANCELLED = _ref[2];

  column = function(size, content, parent) {
    var brd, col;
    if (parent == null) {
      parent = null;
    }
    brd = {
      type: "div",
      cls: "breadcrumb",
      children: content
    };
    col = {
      type: "div",
      cls: size + " column",
      children: brd
    };
    return _mapper.parseMapForParent(col, parent);
  };

  statusColour = function(status) {
    if (status === ACTIVE) {
      return "text-green";
    }
    if (status === PAUSED) {
      return "text-yellow";
    }
    if (status === CANCELLED) {
      return "text-red";
    }
    return "text-mute";
  };

  actionName = function(status) {
    if (status === ACTIVE) {
      return "Pause";
    }
    if (status === PAUSED) {
      return "Resume";
    }
    return null;
  };

  columnStatus = function(status, colour) {
    var section, st;
    st = {
      type: "div",
      cls: "" + colour,
      title: "" + status
    };
    section = {
      type: "div",
      cls: "section",
      children: st
    };
    return column("one-sixth", section);
  };

  columnName = function(uid, name) {
    var nm, section;
    nm = {
      type: "a",
      href: "/timetable?id=" + uid + "&mode=show",
      title: "" + name
    };
    section = {
      type: "div",
      cls: "section",
      children: nm
    };
    return column("one-third", section);
  };

  columnStats = function(numJobs, jobid, timestamp) {
    var counter, countertext, section1, section2, time;
    counter = {
      type: "span",
      title: "" + numJobs
    };
    countertext = {
      type: "span",
      cls: "text-mute",
      title: " scheduled jobs"
    };
    section1 = {
      type: "div",
      cls: "section",
      children: [counter, countertext]
    };
    section2 = null;
    if (timestamp && timestamp > 0) {
      jobid = {
        type: "a",
        href: "/job?jobid=" + jobid,
        title: "latest "
      };
      time = {
        type: "span",
        title: "" + (_util.timestampToDate(timestamp))
      };
      section2 = {
        type: "div",
        cls: "section",
        children: [jobid, time]
      };
    }
    return column("one-third", [section1, section2]);
  };

  columnAction = function(uid, name, status, action) {
    var btn, section;
    btn = {
      type: "div",
      cls: "btn btn-compact",
      title: "" + name,
      onclick: function() {
        this.uid = uid;
        this.status = status;
        return typeof action === "function" ? action(this) : void 0;
      }
    };
    section = {
      type: "div",
      cls: "section",
      children: btn
    };
    return column("one-sixth", section);
  };

  row = function(obj) {
    var aname, colAction, colName, colStats, colStatus, jobid, name, numJobs, status, timestamp, uid;
    uid = obj["uid"];
    name = obj["name"];
    numJobs = obj["numjobs"];
    status = obj["status"];
    jobid = obj["latestjobid"];
    timestamp = obj["latestruntime"];
    colStatus = columnStatus(status, statusColour(status));
    colName = columnName(uid, name);
    colStats = columnStats(numJobs, jobid, timestamp);
    colAction = null;
    aname = actionName(status);
    if (aname) {
      colAction = columnAction(uid, aname, status, function(obj) {
        var fetch, update;
        fetch = (function(_this) {
          return function() {
            _util.addClass(obj, "btn-disabled");
            return obj.innerHTML = "???";
          };
        })(this);
        update = (function(_this) {
          return function(ok) {
            _util.addClass(obj, "btn-disabled");
            if (ok) {
              return obj.innerHTML = obj.status === ACTIVE ? "Paused" : "Active";
            } else {
              return obj.innerHTML = "Error";
            }
          };
        })(this);
        if (obj.status === ACTIVE) {
          return _timetableApi.pause(obj.uid, (function() {
            return fetch();
          }), (function(ok, json) {
            return update(ok);
          }));
        } else if (obj.status === PAUSED) {
          return _timetableApi.resume(obj.uid, (function() {
            return fetch();
          }), (function(ok, json) {
            return update(ok);
          }));
        }
      });
    }
    return _misc.segment(_misc.columns([colStatus, colName, colStats, colAction]));
  };

  update = function(statuses) {
    return _timetableApi.list(false, statuses, function() {
      return timetablesElem.innerHTML = "";
    }, function(ok, json) {
      var msg, result, rows, timetable, timetables, view;
      if (ok) {
        timetables = json["content"]["timetables"];
        if (timetables && timetables.length > 0) {
          rows = [
            (function() {
              var _i, _len, _results;
              _results = [];
              for (_i = 0, _len = timetables.length; _i < _len; _i++) {
                timetable = timetables[_i];
                _results.push(row(timetable));
              }
              return _results;
            })()
          ];
          return _misc.segments(rows, timetablesElem);
        } else {
          view = _misc.blankslateWithMsg("No timetables found :(", "You can create a timetable for any job from job details view");
          return _mapper.parseMapForParent(view, timetablesElem);
        }
      } else {
        msg = json ? json["content"]["msg"] : "We know and keep working on that";
        result = _misc.blankslateWithMsg("Something went wrong :(", msg);
        return _mapper.parseMapForParent(result, timetablesElem);
      }
    });
  };

  noncancelled = document.getElementById("octohaven-timetables-noncancelled");

  active = document.getElementById("octohaven-timetables-active");

  paused = document.getElementById("octohaven-timetable-paused");

  cancelled = document.getElementById("octohaven-timetable-cancelled");

  resetLabels = function() {
    _util.removeClass(noncancelled, "selected");
    _util.removeClass(active, "selected");
    _util.removeClass(paused, "selected");
    return _util.removeClass(cancelled, "selected");
  };

  selectLabel = function(elem) {
    return _util.addClass(elem, "selected");
  };

  actionLabel = function(e, elem, statuses) {
    resetLabels();
    if (typeof update === "function") {
      update(statuses);
    }
    selectLabel(elem);
    if (e != null) {
      e.preventDefault();
    }
    return e != null ? e.stopPropagation() : void 0;
  };

  _util.addEventListener(noncancelled, "click", function(e) {
    return actionLabel(e, noncancelled, [ACTIVE, PAUSED]);
  });

  _util.addEventListener(active, "click", function(e) {
    return actionLabel(e, active, [ACTIVE]);
  });

  _util.addEventListener(paused, "click", function(e) {
    return actionLabel(e, paused, [PAUSED]);
  });

  _util.addEventListener(cancelled, "click", function(e) {
    return actionLabel(e, cancelled, [CANCELLED]);
  });

  actionLabel(null, noncancelled, [ACTIVE, PAUSED]);

}).call(this);
