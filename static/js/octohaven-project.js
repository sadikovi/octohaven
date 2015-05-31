// Generated by CoffeeScript 1.9.0
(function() {
  var addbrancheditor, branches_map, branchesaddb, branchesform, brancheslist, convertTimeStampIntoRuntime, createBranch, deleteBranch, deleteLink, error_map, nameeditor, nameelem, no_branches_map, project_hash, project_name, reloadBranchesForm, setDefault;

  project_name = function() {
    var a, x, _i, _len;
    a = document.getElementsByTagName("meta");
    for (_i = 0, _len = a.length; _i < _len; _i++) {
      x = a[_i];
      if (x.name === "projectname") {
        return x.getAttribute("content");
      }
    }
  };

  project_hash = function() {
    var a, x, _i, _len;
    a = document.getElementsByTagName("meta");
    for (_i = 0, _len = a.length; _i < _len; _i++) {
      x = a[_i];
      if (x.name === "projecthash") {
        return x.getAttribute("content");
      }
    }
  };

  nameelem = document.getElementById("octohaven-project-desc");

  deleteLink = document.getElementById("octohaven-project-action-delete");

  if (!nameelem) {
    throw new Error("Project name element is undefined");
  }

  nameeditor = new this.FastEditor(nameelem, (function(_this) {
    return function(status, value) {
      var data;
      if (status && value) {
        data = {
          projectname: "" + (_this.util.quote(project_name())),
          projectdesc: "" + (_this.util.quote(value))
        };
        return _this.loader.sendrequest("post", "/api/project/update", {}, JSON.stringify(data));
      }
    };
  })(this));

  this.util.addEventListener(deleteLink, "click", (function(_this) {
    return function(e) {
      var data;
      e.preventDefault();
      data = {
        projectname: "" + (_this.util.quote(project_name()))
      };
      return _this.loader.sendrequest("post", "/api/project/delete", {}, JSON.stringify(data), function(s, r) {
        var isdeleted, redirect, response, _ref;
        if (s === 200) {
          response = JSON.parse(r);
          _ref = [response.data.redirect, response.data.isdeleted], redirect = _ref[0], isdeleted = _ref[1];
          return window.location.href = redirect ? redirect : "/";
        } else {
          return console.log("General error happened due to project deletion");
        }
      }, function(e, r) {
        return console.log("Error " + r);
      });
    };
  })(this));

  branchesform = document.getElementById("octohaven-branches-form");

  brancheslist = document.getElementById("octohaven-branches-list");

  branchesaddb = document.getElementById("octohaven-branches-addb");

  if (!(branchesform && brancheslist && branchesaddb)) {
    throw new Error("Branches form or its elements are undefined");
  }

  no_branches_map = function() {
    var header, map, paragraph;
    return map = {
      type: "div",
      cls: "blankslate",
      children: [
        header = {
          type: "h1",
          cls: "text-thin",
          title: "No branches"
        }, paragraph = {
          type: "p",
          cls: "text-mute",
          title: "Add one with [+ branch]"
        }
      ]
    };
  };

  branches_map = function(branches) {
    var x, _branches_map, _one_branch;
    _one_branch = function(branch) {
      var default_t, delete_t, edited, isdefault, isdelete, name, _b_default, _b_delete, _ref, _ref1;
      if (branch["default"]) {
        _ref = ["DEFAULT", "---"], default_t = _ref[0], delete_t = _ref[1];
      } else {
        _ref1 = ["[ Set ]", "[ Delete ]"], default_t = _ref1[0], delete_t = _ref1[1];
      }
      _b_default = {
        type: "a",
        href: "",
        title: "" + default_t
      };
      _b_delete = {
        type: "a",
        href: "",
        title: "" + delete_t
      };
      _b_default = this.mapper.parseMapForParent(_b_default);
      _b_default._branch = branch;
      _b_delete = this.mapper.parseMapForParent(_b_delete);
      _b_delete._branch = branch;
      this.util.addEventListener(_b_default, "click", function(e) {
        return e.preventDefault();
      });
      if (branch["default"]) {
        _b_default = {
          type: "span",
          cls: "text-emphasized",
          title: "Default"
        };
        _b_delete = null;
      } else {
        this.util.addEventListener(_b_default, "click", function(e) {
          e.preventDefault();
          return typeof setDefault === "function" ? setDefault(this._branch) : void 0;
        });
        this.util.addEventListener(_b_delete, "click", function(e) {
          e.preventDefault();
          return typeof deleteBranch === "function" ? deleteBranch(this._branch) : void 0;
        });
      }
      return branch = {
        type: "div",
        cls: "segment",
        children: {
          type: "div",
          cls: "columns",
          children: [
            name = {
              type: "div",
              cls: "one-fifth column",
              children: {
                type: "div",
                cls: "segment",
                children: {
                  type: "a",
                  href: branch.link,
                  title: branch.name
                }
              }
            }, edited = {
              type: "div",
              cls: "two-fifths column",
              children: {
                type: "div",
                cls: "segment",
                title: typeof convertTimeStampIntoRuntime === "function" ? convertTimeStampIntoRuntime(branch.edited) : void 0
              }
            }, isdefault = {
              type: "div",
              cls: "one-fifth column",
              children: {
                type: "div",
                cls: "segment",
                children: [_b_default]
              }
            }, isdelete = {
              type: "div",
              cls: "one-fifth column",
              children: {
                type: "div",
                cls: "segment",
                children: [_b_delete]
              }
            }
          ]
        }
      };
    };
    if (branches && branches.length) {
      return _branches_map = {
        type: "div",
        cls: "segments",
        children: (function() {
          var _i, _len, _results;
          _results = [];
          for (_i = 0, _len = branches.length; _i < _len; _i++) {
            x = branches[_i];
            _results.push(_one_branch(x));
          }
          return _results;
        })()
      };
    } else {
      return no_branches_map();
    }
  };

  error_map = function(msg) {
    var header, map, paragraph, reload;
    if (msg == null) {
      msg = "Cannot fetch branches.";
    }
    return map = {
      type: "div",
      cls: "blankslate",
      children: [
        header = {
          type: "h1",
          cls: "text-thin",
          title: "Something went wrong"
        }, paragraph = {
          type: "p",
          cls: "text-mute",
          title: "" + msg
        }, reload = {
          type: "p",
          cls: "text-mute",
          children: {
            type: "a",
            title: "Reload branches",
            href: "",
            onclick: function(e) {
              if (typeof reloadBranchesForm === "function") {
                reloadBranchesForm();
              }
              return e.preventDefault();
            }
          }
        }
      ]
    };
  };

  reloadBranchesForm = function(link, data) {
    data = data || {
      projectname: project_name(),
      branchname: "",
      projecthash: project_hash()
    };
    brancheslist.innerHTML = "";
    this.util.addClass(brancheslist, "loading");
    link = link || "/api/branch/select";
    return this.loader.sendrequest("post", link, {}, JSON.stringify(data), (function(_this) {
      return function(s, r) {
        if (s === 200) {
          r = JSON.parse(r);
          _this.mapper.parseMapForParent(branches_map(r.data.branches), brancheslist);
        } else {
          _this.mapper.parseMapForParent(error_map(), brancheslist);
        }
        return _this.util.removeClass(brancheslist, "loading");
      };
    })(this), (function(_this) {
      return function(e, r) {
        var msg;
        if (e === 400) {
          msg = JSON.parse(r).message;
        }
        _this.mapper.parseMapForParent(error_map(msg), brancheslist);
        return _this.util.removeClass(brancheslist, "loading");
      };
    })(this));
  };

  createBranch = function(branchname) {
    return typeof reloadBranchesForm === "function" ? reloadBranchesForm("/api/branch/create", {
      projectname: project_name(),
      branchname: branchname,
      projecthash: project_hash()
    }) : void 0;
  };

  setDefault = function(branch) {
    return typeof reloadBranchesForm === "function" ? reloadBranchesForm("/api/branch/default", {
      projectname: project_name(),
      branchname: branch.name,
      projecthash: project_hash()
    }) : void 0;
  };

  deleteBranch = function(branch) {
    return typeof reloadBranchesForm === "function" ? reloadBranchesForm("/api/branch/delete", {
      projectname: project_name(),
      branchname: branch.name,
      projecthash: project_hash()
    }) : void 0;
  };

  convertTimeStampIntoRuntime = function(timestamp) {
    var date, diff, now, _ref;
    _ref = [new Date, new Date(timestamp * 1000)], now = _ref[0], date = _ref[1];
    diff = (now.getTime() - date.getTime()) / 1000.0;
    if ((0 < diff && diff < 60)) {
      return "Edited less than a minute ago";
    } else if ((60 <= diff && diff < 60 * 60)) {
      return "Edited " + (Math.round(diff / 60)) + " minutes ago";
    } else if ((60 * 60 <= diff && diff < 24 * 60 * 60)) {
      return "Edited " + (Math.round(diff / 60 / 60)) + " hours ago";
    } else {
      return "Edited on " + (date.toLocaleString("en-nz"));
    }
  };

  if (typeof reloadBranchesForm === "function") {
    reloadBranchesForm();
  }

  addbrancheditor = new this.FastEditor(branchesaddb, function(status, value) {
    if (status) {
      return typeof createBranch === "function" ? createBranch(value) : void 0;
    }
  }, "Create", "Cancel", "New branch name", false);

}).call(this);
