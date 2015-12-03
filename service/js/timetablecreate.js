(function() {
  var DEFAULT_TIMETABLE, IS_SUBMITTED, controlBar, cronHelpElem, currentTimetable, id, mode, params, setLoadStatus, setSubmitStatus, setTextStatus, statusBar, submitBtn, submitTimetable, timetableCreateElem, view, _jobapi, _mapper, _misc, _namer, _timetableApi, _util;

  timetableCreateElem = document.getElementById("octohaven-timetable-create");

  cronHelpElem = document.getElementById("octohaven-cron-help");

  if (!(timetableCreateElem && cronHelpElem)) {
    throw new Error("Timetable placeholders are not found");
  }

  _mapper = this.mapper;

  _util = this.util;

  _misc = this.misc;

  _namer = this.namer;

  _jobapi = new this.JobApi;

  _timetableApi = new this.TimetableApi;

  params = _util.windowParameters();

  mode = params != null ? params.mode : void 0;

  id = params != null ? params.id : void 0;

  if (mode !== "create") {
    view = _misc.blankslateWithMsg("Something went wrong :(", "Unrecognized mode");
    _mapper.parseMapForParent(view, timetableCreateElem);
    return;
  }

  if (!id) {
    view = _misc.blankslateWithMsg("Something went wrong :(", "Undefined id");
    _mapper.parseMapForParent(view, timetableCreateElem);
    return;
  }

  controlBar = document.getElementById("octohaven-create-controls");

  submitBtn = document.getElementById("octohaven-submit-timetable");

  statusBar = document.getElementById("octohaven-validation-status");

  if (!(controlBar && statusBar && submitBtn)) {
    throw new Error("Submit requirements failed");
  }

  IS_SUBMITTED = false;

  DEFAULT_TIMETABLE = new this.Timetable({
    "name": "Timetable " + (_namer.generate()),
    "pattern": "",
    "jobid": "",
    "jobname": "Undefined"
  });

  currentTimetable = DEFAULT_TIMETABLE;

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

  submitTimetable = function(timetable) {
    var settings;
    setLoadStatus(true);
    if (!IS_SUBMITTED) {
      IS_SUBMITTED = true;
      settings = timetable.settings;
      return _timetableApi.submit(settings, null, function(ok, content) {
        var body, msg, uid;
        setLoadStatus(false);
        if (ok) {
          msg = content["content"]["msg"];
          uid = content["content"]["uid"];
          body = {
            type: "span",
            title: msg + ". ",
            children: {
              type: "a",
              title: "View details",
              href: "/timetable?id=" + uid + "&mode=show"
            }
          };
          return setSubmitStatus(ok, body);
        } else {
          IS_SUBMITTED = false;
          msg = content ? content["content"]["msg"] : "Something went wrong :(";
          return setTextStatus(ok, msg);
        }
      });
    } else {
      setTextStatus(false, "You cannot resubmit the timetable");
      return setLoadStatus(false);
    }
  };

  _util.addEventListener(submitBtn, "click", function(e) {
    submitTimetable(currentTimetable);
    e.preventDefault();
    return e.stopPropagation();
  });

  _jobapi.getJob(id, function() {
    return timetableCreateElem.innerHTML = "";
  }, function(ok, json) {
    var job, jobid, jobname, msg, result, rows;
    result = null;
    if (ok) {
      _util.removeClass(controlBar, "hidden");
      _util.removeClass(statusBar, "hidden");
      _util.removeClass(cronHelpElem, "hidden");
      job = json["content"]["job"];
      jobid = job["uid"];
      jobname = job["sparkjob"]["name"];
      currentTimetable.set("jobid", jobid);
      currentTimetable.set("jobname", jobname);
      rows = [
        _misc.staticOption("Clone job", "Base job for timetable", {
          type: "a",
          href: "/job?jobid=" + jobid,
          title: "" + jobname
        }), _misc.dynamicOption("Name", "Timetable name", "" + (currentTimetable.get("name")), function(status, value) {
          if (status) {
            return currentTimetable.set("name", value);
          }
        }), _misc.dynamicOption("Cron pattern", "Cron expression for scheduling", "" + (currentTimetable.get("pattern")), function(status, value) {
          if (status) {
            return currentTimetable.set("pattern", value);
          }
        })
      ];
      result = _misc.segments(rows);
    } else {
      msg = json ? json["content"]["msg"] : "We know and keep working on that";
      result = _misc.blankslateWithMsg("Something went wrong :(", msg);
    }
    return _mapper.parseMapForParent(result, timetableCreateElem);
  });

}).call(this);
