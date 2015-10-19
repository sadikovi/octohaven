// Generated by CoffeeScript 1.9.0
(function() {
  var CurrentJob, JOB_CREATE, JOB_SUBMIT, breadcrumbs, breadcrumbsElem, currentJob, files, filesElem, jobCanvas, jobSettingElem, selectJar, selectedJarElem, setLoadStatus, setSubmitStatus, setTextStatus, settings, statusBar, statuses, submitBtn, submitJob, _filelist, _mapper, _namer, _ref, _util,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  _filelist = new this.Filelist;

  _util = this.util;

  _mapper = this.mapper;

  _namer = this.namer;

  jobCanvas = document.getElementById("octohaven-job-settings");

  if (!jobCanvas) {
    throw new Error("Job settings canvas is undefined");
  }

  breadcrumbsElem = document.getElementById("octohaven-filelist-breadcrumbs");

  filesElem = document.getElementById("octohaven-filelist-files");

  selectedJarElem = document.getElementById("octohaven-selected-jar");

  if (!(breadcrumbsElem && filesElem && selectedJarElem)) {
    throw new Error("Cannot build file list");
  }

  submitBtn = document.getElementById("octohaven-submit-job");

  statusBar = document.getElementById("octohaven-validation-status");

  if (!(submitBtn && statusBar)) {
    throw new Error("Submit requirements failed");
  }

  _ref = ["CREATE", "SUBMIT"], JOB_CREATE = _ref[0], JOB_SUBMIT = _ref[1];

  statuses = [JOB_CREATE, JOB_SUBMIT];

  CurrentJob = (function() {
    function CurrentJob(name, mainClass, driverMemory, executorMemory, options, jobconf) {
      this.settings = {
        name: "" + name,
        mainClass: "" + mainClass,
        driverMemory: "" + driverMemory,
        executorMemory: "" + executorMemory,
        options: "" + options,
        jobconf: "" + jobconf
      };
      this.jar = {
        elem: null,
        path: ""
      };
      this.status = JOB_CREATE;
    }

    CurrentJob.prototype.setStatus = function(status) {
      if (__indexOf.call(statuses, status) < 0) {
        throw new Error("Invalid status " + status);
      }
      return this.status = status;
    };

    CurrentJob.prototype.getStatus = function() {
      return this.status;
    };

    CurrentJob.prototype.setJar = function(elem, path) {
      this.jar.elem = elem;
      return this.jar.path = path;
    };

    CurrentJob.prototype.isJarSet = function() {
      return this.jar.elem != null;
    };

    CurrentJob.prototype.getJarElem = function() {
      return this.jar.elem;
    };

    CurrentJob.prototype.getJarPath = function() {
      return this.jar.path;
    };

    CurrentJob.prototype.setOption = function(key, value) {
      if (!(key in this.settings)) {
        throw new Error("Option is not found");
      }
      return this.settings[key] = value;
    };

    CurrentJob.prototype.getOption = function(key) {
      if (key in this.settings) {
        return this.settings[key];
      } else {
        return null;
      }
    };

    return CurrentJob;

  })();

  currentJob = new CurrentJob(_namer.generate(), "org.test.Main", "8g", "8g", "", "");

  jobSettingElem = function(name, desc, value, canChange, onValueChanged) {
    var block, body, changer, header, span, trigger;
    if (canChange == null) {
      canChange = true;
    }
    span = _mapper.parseMapForParent({
      type: "span",
      cls: "text-mute tooltipped tooltipped-n",
      title: "" + name
    });
    span.setAttribute("aria-label", "" + desc);
    header = {
      type: "div",
      cls: "one-fifth column",
      children: span
    };
    body = _mapper.parseMapForParent({
      type: "div",
      cls: "three-fifths column",
      title: "" + value
    });
    body.setAttribute("data-attr", "fast-editor-texter");
    trigger = _mapper.parseMapForParent({
      type: "a",
      href: "#",
      title: "Change"
    });
    trigger.setAttribute("data-attr", "fast-editor-trigger");
    changer = _mapper.parseMapForParent(canChange ? {
      type: "div",
      cls: "one-fifth column",
      children: trigger
    } : null);
    block = _mapper.parseMapForParent({
      type: "div",
      cls: "segment",
      children: {
        type: "div",
        cls: "columns",
        children: [header, changer, body]
      }
    });
    block.setAttribute("data-attr", "fast-editor");
    if (canChange) {
      new this.FastEditor(block, function(status, value) {
        return typeof onValueChanged === "function" ? onValueChanged(status, value) : void 0;
      });
    }
    return block;
  };

  settings = {
    type: "div",
    cls: "segments",
    children: [
      jobSettingElem("Job name", "Friendly job name", currentJob.getOption("name"), true, function(ok, value) {
        if (ok) {
          return currentJob.setOption("name", value);
        }
      }), jobSettingElem("Main class", "Main class as entrypoint for the job.", currentJob.getOption("mainClass"), true, function(ok, value) {
        if (ok) {
          return currentJob.setOption("mainClass", value);
        }
      }), jobSettingElem("Driver memory", "Memory for operations in a driver programme", currentJob.getOption("driverMemory"), true, function(ok, value) {
        if (ok) {
          return currentJob.setOption("driverMemory", value);
        }
      }), jobSettingElem("Executor memory", "Amount of memory for Spark executors", currentJob.getOption("executorMemory"), true, function(ok, value) {
        if (ok) {
          return currentJob.setOption("executorMemory", value);
        }
      }), jobSettingElem("Options", "Additional settings, e.g. JVM, networking, shuffle...", currentJob.getOption("options"), true, function(ok, value) {
        if (ok) {
          return currentJob.setOption("options", value);
        }
      }), jobSettingElem("Job options", "Specific job [not Spark] options to pass to entrypoint", currentJob.getOption("jobconf"), true, function(ok, value) {
        if (ok) {
          return currentJob.setOption("jobconf", value);
        }
      })
    ]
  };

  _mapper.parseMapForParent(settings, jobCanvas);

  breadcrumbs = function(dir) {
    return _filelist.breadcrumbs(dir, function() {
      return breadcrumbsElem.innerHTML = "";
    }, (function(_this) {
      return function(ok, json) {
        var arr, elem, i, ls, obj, _i, _len, _ref1;
        if (ok) {
          _ref1 = [[], json["content"]["breadcrumbs"]], arr = _ref1[0], ls = _ref1[1];
          for (i = _i = 0, _len = ls.length; _i < _len; i = ++_i) {
            obj = ls[i];
            if (i < ls.length - 1) {
              elem = {
                type: "a",
                cls: "section",
                title: "" + obj["name"],
                onclick: function(e) {
                  breadcrumbs(this.path);
                  return files(this.path);
                }
              };
              elem = _mapper.parseMapForParent(elem);
              elem.path = obj["path"];
              arr.push(elem);
              arr.push({
                type: "div",
                cls: "separator",
                title: "/"
              });
            } else {
              arr.push({
                type: "div",
                cls: "active section",
                title: "" + obj["name"]
              });
            }
          }
          return _mapper.parseMapForParent(arr, breadcrumbsElem);
        } else if (json) {
          return setTextStatus(json["content"]["msg"], false);
        } else {
          return setTextStatus("Something went wrong :(", false);
        }
      };
    })(this));
  };

  selectJar = function(elem, path) {
    if (currentJob.isJarSet()) {
      _util.removeClass(currentJob.getJarElem(), "selected");
      selectedJarElem.innerHTML = "";
    }
    currentJob.setJar(elem, path);
    _util.addClass(elem, "selected");
    return selectedJarElem.innerHTML = path;
  };

  files = function(dir) {
    return _filelist.files(dir, function() {
      return filesElem.innerHTML = "";
    }, (function(_this) {
      return function(ok, json) {
        var arr, elem, ls, obj, _i, _len, _ref1;
        if (ok) {
          _ref1 = [[], json["content"]["list"]], arr = _ref1[0], ls = _ref1[1];
          for (_i = 0, _len = ls.length; _i < _len; _i++) {
            obj = ls[_i];
            elem = {
              type: "a",
              cls: "menu-item",
              href: ""
            };
            if (obj["tp"] === "DIR") {
              elem["title"] = "[dir] " + obj["name"];
              elem["onclick"] = function(e) {
                breadcrumbs(this.obj["path"]);
                files(this.obj["path"]);
                e.preventDefault();
                return e.stopPropagation();
              };
            } else {
              elem["title"] = "[jar] " + obj["name"];
              elem["onclick"] = function(e) {
                selectJar(this, this.obj["path"]);
                e.preventDefault();
                return e.stopPropagation();
              };
            }
            elem = _mapper.parseMapForParent(elem);
            elem.obj = obj;
            if (currentJob.getJarPath() === elem.obj["path"]) {
              selectJar(elem, elem.obj["path"]);
            }
            arr.push(elem);
          }
          return _mapper.parseMapForParent(arr, filesElem);
        } else if (json) {
          return setTextStatus(json["content"]["msg"], false);
        } else {
          return setTextStatus("Something went wrong :(", false);
        }
      };
    })(this));
  };

  breadcrumbs("");

  files("");

  setLoadStatus = function(load) {
    if (load) {
      return _util.addClass(statusBar, "loading");
    } else {
      return _util.removeClass(statusBar, "loading");
    }
  };

  setSubmitStatus = function(ok, internal) {
    var mode, obj;
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

  submitJob = function(job) {
    var resolver;
    setLoadStatus(true);
    if (job.getStatus() === JOB_CREATE) {
      job.setStatus(JOB_SUBMIT);
      settings = job.settings;
      settings["jar"] = job.jar.path;
      resolver = new JobResolver;
      return resolver.submit(JSON.stringify(settings), null, function(ok, content) {
        var body, jobid, msg;
        setLoadStatus(false);
        if (ok) {
          msg = content["content"]["msg"];
          jobid = content["content"]["jobid"];
          body = {
            type: "span",
            title: msg + ". ",
            children: {
              type: "a",
              title: "View details",
              href: "/job?=" + jobid
            }
          };
          return setSubmitStatus(ok, body);
        } else {
          job.setStatus(JOB_CREATE);
          msg = content ? content["content"]["msg"] : "Something went wrong :(";
          return setTextStatus(ok, msg);
        }
      });
    } else {
      setTextStatus(false, "You cannot resubmit the job");
      return setLoadStatus(false);
    }
  };

  _util.addEventListener(submitBtn, "click", function(e) {
    submitJob(currentJob);
    e.preventDefault();
    return e.stopPropagation();
  });

}).call(this);
