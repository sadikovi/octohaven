(function() {
  var cancelBtn, cancelTimetable, column, id, keyElem, keyValue, mode, params, setLoadStatus, setSubmitStatus, setTextStatus, showControls, statusBar, timeToDate, timetableShowElem, view, _mapper, _misc, _timetableLoader, _util;

  timetableShowElem = document.getElementById("octohaven-timetable-show");

  if (!timetableShowElem) {
    throw new Error("Timetable placeholders are not found");
  }

  _mapper = this.mapper;

  _util = this.util;

  _misc = this.misc;

  _timetableLoader = new this.TimetableLoader;

  params = _util.windowParameters();

  mode = params != null ? params.mode : void 0;

  id = params != null ? params.id : void 0;

  if (mode !== "show") {
    view = _misc.blankslateWithMsg("Something went wrong :(", "Unrecognized mode");
    _mapper.parseMapForParent(view, timetableShowElem);
    return;
  }

  if (id === null) {
    view = _misc.blankslateWithMsg("Something went wrong :(", "Undefined id");
    _mapper.parseMapForParent(view, timetableShowElem);
    return;
  }

  showControls = document.getElementById("octohaven-show-controls");

  statusBar = document.getElementById("octohaven-validation-status");

  cancelBtn = document.getElementById("octohaven-cancel-timetable");

  if (!(showControls && cancelBtn && statusBar)) {
    throw new Error("Control requirements failed");
  }

  setLoadStatus = function(load) {
    if (load) {
      return _util.addClass(statusBar, "loading");
    } else {
      return _util.removeClass(statusBar, "loading");
    }
  };

  setSubmitStatus = function(ok, internal) {
    var obj;
    statusBar.innerHTML = "";
    mode = ok ? "success-box" : "error-box";
    obj = {
      type: "div",
      cls: mode,
      children: internal
    };
    return _mapper.parseMapForParent(obj, statusBar);
  };

  setTextStatus = function(ok, text) {
    return setSubmitStatus(ok, {
      type: "span",
      title: "" + text
    });
  };

  cancelTimetable = function(uid) {
    setLoadStatus(true);
    return _timetableLoader.cancel(uid, null, function(ok, content) {
      var msg;
      setLoadStatus(false);
      msg = content ? content["content"]["msg"] : "Something went wrong :(";
      return setTextStatus(ok, msg);
    });
  };

  column = function(width, content, parent) {
    var col;
    if (parent == null) {
      parent = null;
    }
    col = {
      type: "div",
      cls: width + " column",
      children: content
    };
    return _mapper.parseMapForParent(col, parent);
  };

  keyElem = function(key, desc, elem) {
    var keyElement, list;
    keyElement = _mapper.parseMapForParent({
      type: "span",
      cls: "text-mute tooltipped tooltipped-n",
      title: "" + key
    });
    keyElement.setAttribute("aria-label", "" + desc);
    list = [
      column("one-fourth", keyElement), column("three-fourths", {
        type: "span",
        children: elem
      })
    ];
    return _misc.segment(_misc.columns(list));
  };

  keyValue = function(key, desc, value) {
    return keyElem(key, desc, {
      type: "span",
      title: "" + value
    });
  };

  timeToDate = function(timestamp, alter) {
    if (timestamp > 0) {
      return _util.timestampToDate(timestamp);
    }
    return "" + alter;
  };

  _timetableLoader.get(id, function() {
    return timetableShowElem.innerHTML = "";
  }, function(ok, json) {
    var job, jobid, jobname, msg, result, rows, timetable;
    result = null;
    if (ok) {
      _util.removeClass(statusBar, "hidden");
      _util.removeClass(showControls, "hidden");
      timetable = json["content"]["timetable"];
      job = json["content"]["job"];
      jobid = job["uid"];
      jobname = job["sparkjob"]["name"];
      rows = [
        keyValue("Timetable id", "Timetable id", timetable["uid"]), keyValue("Name", "Timetable name", timetable["name"]), keyValue("Status", "Timetable status", timetable["status"]), keyElem("Clone job", "Job that is used to create jobs for timetable", {
          type: "a",
          href: "/job?jobid=" + jobid,
          title: "" + jobname
        }), keyValue("Cron expression", "Timetable schedule as Cron expression", timetable["crontab"]["pattern"]), keyValue("Start time", "Start time for timetable", timeToDate(timetable["starttime"], "None")), keyValue("Stop time", "Stop time for timetable (if cancelled)", timeToDate(timetable["stoptime"], "None")), keyValue("Number of jobs run", "Number of actual jobs having run", timetable["numjobs"]), keyElem("Latest scheduled job", "Latest scheduled job for timetable", {
          type: "a",
          href: "/job?jobid=" + timetable.latestjobid,
          title: "view"
        }), keyValue("Latest run", "Latest run (if any)", timeToDate(timetable["stoptime"], "None"))
      ];
      result = _misc.segments(rows);
      if (timetable["status"] === "CANCELLED") {
        _util.addClass(cancelBtn, "btn-disabled");
      } else {
        cancelBtn.uid = timetable["uid"];
        _util.addEventListener(cancelBtn, "click", function(e) {
          cancelTimetable(this.uid);
          e.preventDefault();
          return e.stopPropagation();
        });
      }
    } else {
      msg = json ? json["content"]["msg"] : "We know and keep working on that";
      result = _misc.blankslateWithMsg("Something went wrong :(", msg);
    }
    return _mapper.parseMapForParent(result, timetableShowElem);
  });

}).call(this);
