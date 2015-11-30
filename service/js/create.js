(function() {
  var DEFAULT_TEMPLATE, IS_SUBMITTED, breadcrumbs, breadcrumbsElem, createTemplate, currentJob, delayElem, delayEntry, delays, deleteTemplate, files, filesElem, initColumns, initRow, jobCanvas, jobOption, lastSelectedJarElem, loadTemplate, ls, selectedJarElem, setLoadStatus, setSubmitStatus, setTextStatus, showTemplates, statusBar, submitBtn, submitJob, templateButton, templateHeading, templateRow, _filelist, _mapper, _namer, _util;

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

  delayElem = document.getElementById("octohaven-job-delay");

  if (!delayElem) {
    throw new Error("Cannot find delay element");
  }

  templateHeading = document.getElementById("octohaven-templates");

  templateButton = document.getElementById("octohaven-save-template");

  if (!(templateHeading && templateButton)) {
    throw new Error("Cannot find template elements");
  }

  submitBtn = document.getElementById("octohaven-submit-job");

  statusBar = document.getElementById("octohaven-validation-status");

  if (!(submitBtn && statusBar)) {
    throw new Error("Submit requirements failed");
  }

  IS_SUBMITTED = false;

  DEFAULT_TEMPLATE = new this.Template({
    "name": _namer.generate(),
    "entrypoint": "org.test.Main",
    "driver-memory": "8g",
    "executor-memory": "8g",
    "options": "",
    "jobconf": "",
    "delay": "0",
    "jar": ""
  });

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

  initColumns = function(children) {
    var cols;
    cols = {
      type: "div",
      cls: "columns",
      children: children
    };
    return _mapper.parseMapForParent(cols);
  };

  initRow = function(columns) {
    var row;
    row = {
      type: "div",
      cls: "segment",
      children: columns
    };
    return _mapper.parseMapForParent(row);
  };

  jobOption = function(name, desc, value, onValueChanged) {
    var body, header, row, trigger, triggerLink;
    header = _mapper.parseMapForParent({
      type: "span",
      cls: "text-mute tooltipped tooltipped-n",
      title: "" + name
    });
    header.setAttribute("aria-label", "" + desc);
    header = _mapper.parseMapForParent({
      type: "div",
      cls: "one-fifth column",
      children: header
    });
    triggerLink = _mapper.parseMapForParent({
      type: "a",
      href: "",
      title: "Change"
    });
    triggerLink.setAttribute("data-attr", "fast-editor-trigger");
    trigger = _mapper.parseMapForParent({
      type: "div",
      cls: "one-fifth column",
      children: triggerLink
    });
    body = _mapper.parseMapForParent({
      type: "div",
      cls: "three-fifths column",
      title: "" + value
    });
    body.setAttribute("data-attr", "fast-editor-texter");
    row = initRow(initColumns([header, trigger, body]));
    row.setAttribute("data-attr", "fast-editor");
    new this.FastEditor(row, function(status, value) {
      return typeof onValueChanged === "function" ? onValueChanged(status, value) : void 0;
    });
    return row;
  };

  ls = function(name, cls, path, onClick) {
    var elem, tp;
    tp = onClick ? "a" : "div";
    elem = {
      type: "" + tp,
      cls: "" + cls,
      title: "" + name,
      onclick: function(e) {
        if (typeof onClick === "function") {
          onClick(this);
        }
        e.preventDefault();
        return e.stopPropagation();
      }
    };
    elem = _mapper.parseMapForParent(elem);
    elem.path = path;
    return elem;
  };

  lastSelectedJarElem = null;

  breadcrumbs = function(dir, func, eachElemFunc) {
    return _filelist.breadcrumbs(dir, function() {
      return breadcrumbsElem.innerHTML = "";
    }, (function(_this) {
      return function(ok, json) {
        var arr, elem, i, obj, parts, _i, _len, _ref;
        if (ok) {
          _ref = [[], json["content"]["breadcrumbs"]], arr = _ref[0], parts = _ref[1];
          for (i = _i = 0, _len = parts.length; _i < _len; i = ++_i) {
            obj = parts[i];
            if (i < parts.length - 1) {
              elem = ls(obj["name"], "section", obj["path"], function(el) {
                if (typeof func === "function" ? func(el) : void 0) {
                  breadcrumbs(el.obj.path, func, eachElemFunc);
                  return files(el.obj.path, func, eachElemFunc);
                }
              });
              elem.obj = obj;
              if (typeof eachElemFunc === "function") {
                eachElemFunc(elem);
              }
              arr.push(elem);
              arr.push({
                type: "div",
                cls: "separator",
                title: "/"
              });
            } else {
              elem = ls(obj["name"], "active section", obj["path"]);
              elem.obj = obj;
              if (typeof eachElemFunc === "function") {
                eachElemFunc(elem);
              }
              arr.push(elem);
            }
          }
          return _mapper.parseMapForParent(arr, breadcrumbsElem);
        } else if (json) {
          return setTextStatus(false, json["content"]["msg"]);
        } else {
          return setTextStatus(false, "Something went wrong :(");
        }
      };
    })(this));
  };

  files = function(dir, func, eachElemFunc) {
    return _filelist.files(dir, function() {
      return filesElem.innerHTML = "";
    }, (function(_this) {
      return function(ok, json) {
        var arr, elem, obj, parts, _i, _len, _ref;
        if (ok) {
          _ref = [[], json["content"]["list"]], arr = _ref[0], parts = _ref[1];
          for (_i = 0, _len = parts.length; _i < _len; _i++) {
            obj = parts[_i];
            elem = {
              type: "a",
              cls: "menu-item",
              href: "",
              title: "[" + obj.tp + "] " + obj.name
            };
            elem["onclick"] = function(e) {
              if (typeof func === "function" ? func(this) : void 0) {
                breadcrumbs(this.obj.path, func, eachElemFunc);
                files(this.obj.path, func, eachElemFunc);
              }
              e.preventDefault();
              return e.stopPropagation();
            };
            elem = _mapper.parseMapForParent(elem);
            elem.obj = obj;
            if (typeof eachElemFunc === "function") {
              eachElemFunc(elem);
            }
            arr.push(elem);
          }
          return _mapper.parseMapForParent(arr, filesElem);
        } else if (json) {
          return setTextStatus(false, json["content"]["msg"]);
        } else {
          return setTextStatus(false, "Something went wrong :(");
        }
      };
    })(this));
  };

  delayElem.innerHTML = "";

  delayEntry = function(name, delay) {
    var elem, elemMap;
    elemMap = {
      type: "a",
      cls: "menu-item",
      title: "" + name,
      href: ""
    };
    elem = _mapper.parseMapForParent(elemMap, delayElem);
    elem.diff = delay;
    return elem;
  };

  delays = {
    0: delayEntry("Right away", 0),
    600: delayEntry("In 10 minutes", 10 * 60),
    1800: delayEntry("In 30 minutes", 30 * 60),
    3600: delayEntry("In 1 hour", 1 * 60 * 60),
    10800: delayEntry("In 3 hours", 3 * 60 * 60),
    86400: delayEntry("Next day", 24 * 60 * 60)
  };

  loadTemplate = function(job) {
    var addRow, changeDelay, jobRows, key, loadDelay, select, traverse, value;
    jobCanvas.innerHTML = "";
    jobRows = _mapper.parseMapForParent({
      type: "div",
      cls: "segments"
    }, jobCanvas);
    addRow = function(row) {
      return _mapper.parseMapForParent(row, jobRows);
    };
    addRow(jobOption("Job name", "Friendly job name", job.get("name"), function(ok, value) {
      if (ok) {
        return job.set("name", "" + value);
      }
    }));
    addRow(jobOption("Main class", "Entrypoint for the job", job.get("entrypoint"), function(ok, value) {
      if (ok) {
        return job.set("entrypoint", "" + value);
      }
    }));
    addRow(jobOption("Driver memory", "Memory for the driver programme", job.get("driver-memory"), function(ok, value) {
      if (ok) {
        return job.set("driver-memory", "" + value);
      }
    }));
    addRow(jobOption("Executor memory", "Memory for Spark executors", job.get("executor-memory"), function(ok, value) {
      if (ok) {
        return job.set("executor-memory", "" + value);
      }
    }));
    addRow(jobOption("Spark options", "Settings, e.g. JVM, networking, shuffle...", job.get("options"), function(ok, value) {
      if (ok) {
        return job.set("options", "" + value);
      }
    }));
    addRow(jobOption("Job options", "Job options to pass to entrypoint", job.get("jobconf"), function(ok, value) {
      if (ok) {
        return job.set("jobconf", "" + value);
      }
    }));
    selectedJarElem.innerHTML = job.get("jar") !== "" ? "" + (job.get("jar")) : "&nbsp;";
    traverse = function(elem) {
      if (elem.obj.tp === "JAR") {
        job.set("jar", "" + elem.obj.path);
        selectedJarElem.innerHTML = job.get("jar");
        select(elem);
        return false;
      }
      return true;
    };
    select = function(elem) {
      var file;
      file = elem.obj;
      if (file.tp === "JAR" && file.path === job.get("jar")) {
        if (lastSelectedJarElem) {
          _util.removeClass(lastSelectedJarElem, "selected");
        }
        _util.addClass(elem, "selected");
        return lastSelectedJarElem = elem;
      }
    };
    breadcrumbs("", traverse, select);
    files("", traverse, select);
    changeDelay = function(delay) {
      var each, key;
      if (job != null) {
        job.set("delay", delay.diff);
      }
      for (key in delays) {
        each = delays[key];
        _util.removeClass(each, "selected");
      }
      return _util.addClass(delay, "selected");
    };
    loadDelay = function(delay) {
      var diff;
      diff = _util.intOrElse(delay, 0);
      delay = diff in delays ? delays[diff] : delays[0];
      return changeDelay(delay);
    };
    for (key in delays) {
      value = delays[key];
      _util.addEventListener(value, "click", function(e) {
        changeDelay(this);
        e.preventDefault();
        return e.stopPropagation();
      });
    }
    return loadDelay(job.get("delay"));
  };

  submitJob = function(job) {
    var resolver, settings;
    setLoadStatus(true);
    if (!IS_SUBMITTED) {
      IS_SUBMITTED = true;
      settings = job.settings;
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
              href: "/job?jobid=" + jobid
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
      setTextStatus(false, "You cannot resubmit the job");
      return setLoadStatus(false);
    }
  };

  templateRow = function(uid, name, content) {
    var a, delBtn, title;
    delBtn = {
      type: "div",
      cls: "btn btn-link btn-micro tooltipped tooltipped-e",
      onclick: function(e) {
        deleteTemplate(this.uid);
        e.preventDefault();
        return e.stopPropagation();
      }
    };
    delBtn = _mapper.parseMapForParent(delBtn);
    delBtn.innerHTML = "&times;";
    delBtn.uid = uid;
    delBtn.setAttribute("aria-label", "Delete");
    title = {
      type: "span",
      title: "" + name
    };
    a = {
      type: "a",
      href: "",
      cls: "menu-item",
      children: [delBtn, title],
      onclick: function(e) {
        currentJob.settings = this.content;
        loadTemplate(currentJob);
        setTextStatus(true, "Template has been loaded");
        e.preventDefault();
        return e.stopPropagation();
      }
    };
    a = _mapper.parseMapForParent(a);
    a.content = content;
    return a;
  };

  showTemplates = function() {
    var tloader;
    tloader = new TemplateLoader;
    return tloader.show(function() {
      var elem, next, _results;
      elem = templateHeading.nextSibling;
      _results = [];
      while (elem) {
        next = elem.nextSibling;
        elem.parentNode.removeChild(elem);
        _results.push(elem = next);
      }
      return _results;
    }, function(ok, json) {
      var arr, content, item, name, parent, uid, _i, _len, _results;
      parent = templateHeading.parentNode;
      if (ok) {
        arr = json["content"]["templates"];
        _results = [];
        for (_i = 0, _len = arr.length; _i < _len; _i++) {
          item = arr[_i];
          uid = item["uid"];
          name = item["name"];
          content = item["content"];
          _results.push(_mapper.parseMapForParent(templateRow(uid, name, content), parent));
        }
        return _results;
      } else {
        return setTextStatus(ok, "Something went wrong");
      }
    });
  };

  deleteTemplate = function(uid) {
    var tloader;
    tloader = new TemplateLoader;
    return tloader["delete"](uid, null, function(ok, json) {
      var msg;
      msg = ok ? json["content"]["msg"] : "Something went wrong";
      setTextStatus(ok, msg);
      return showTemplates();
    });
  };

  createTemplate = function(name, content) {
    var data, tloader;
    setLoadStatus(true);
    data = {
      name: "" + name,
      content: content
    };
    tloader = new TemplateLoader;
    return tloader.create(JSON.stringify(data), null, function(ok, json) {
      var msg;
      setLoadStatus(false);
      msg = json ? json["content"]["msg"] : "Something went wrong :(";
      setTextStatus(ok, msg);
      if (ok) {
        return showTemplates();
      }
    });
  };

  new this.FastEditor(templateButton, function(status, value) {
    if (status) {
      return createTemplate(value, currentJob.settings);
    }
  }, "Save", "Cancel", "Name of template", false);

  currentJob = DEFAULT_TEMPLATE;

  showTemplates();

  loadTemplate(currentJob);

  _util.addEventListener(submitBtn, "click", function(e) {
    submitJob(currentJob);
    e.preventDefault();
    return e.stopPropagation();
  });

}).call(this);
