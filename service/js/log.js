(function() {
  var askAnotherPage, elem, jobDetailsElem, jobLinkElem, jobLogsElem, jobid, menu, page, params, preContent, type, _jobapi, _logapi, _mapper, _misc, _util,
    __slice = [].slice;

  jobLinkElem = document.getElementById("octohaven-job-link");

  jobDetailsElem = document.getElementById("octohaven-job-details");

  jobLogsElem = document.getElementById("octohaven-job-logs");

  if (!(jobDetailsElem && jobLogsElem && jobLinkElem)) {
    throw new Error("Job detail and log elements are not found");
  }

  _mapper = this.mapper;

  _util = this.util;

  _misc = this.misc;

  _jobapi = new this.JobApi;

  _logapi = new this.LogApi;

  elem = function() {
    var action, args, btn, input, type;
    type = arguments[0], args = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
    if (type === "btn") {
      return _misc.section([
        {
          type: "div",
          cls: "btn " + args[1],
          title: "" + args[0],
          onclick: args[2]
        }
      ]);
    } else if (type === "pair") {
      return _misc.section([
        {
          type: "span",
          cls: "text-mute",
          title: "" + args[0]
        }, {
          type: "span",
          title: "" + args[1]
        }
      ]);
    } else if (type === "input") {
      input = _mapper.parseMapForParent({
        type: "input",
        inputtype: "text",
        cls: "input-squared",
        inputvalue: "" + args[1]
      });
      action = args[2];
      btn = _mapper.parseMapForParent({
        type: "div",
        cls: "btn tooltipped tooltipped-n",
        title: "" + args[0],
        arialabel: "Jump to the page",
        onclick: function() {
          return typeof action === "function" ? action(this.input) : void 0;
        }
      });
      btn.input = input;
      return _misc.section([
        input, {
          type: "div",
          cls: "separator"
        }, btn
      ]);
    } else {
      return null;
    }
  };

  menu = function(info) {
    var action, btnCls, menuElem, next, page, pages, prev;
    page = info["page"];
    pages = info["pages"];
    next = page + 1;
    prev = page - 1;
    btnCls = function(page) {
      if (page < 1 || page > pages) {
        return "btn-disabled";
      } else {
        return "";
      }
    };
    menuElem = {
      type: "div",
      cls: "breadcrumb",
      children: [
        elem("btn", "Prev", "" + (btnCls(prev)), action = function() {
          return askAnotherPage(type, jobid, prev);
        }), elem("btn", "Next", "" + (btnCls(next)), action = function() {
          return askAnotherPage(type, jobid, next);
        }), elem("btn", "Last", "", action = function() {
          return askAnotherPage(type, jobid, pages);
        }), elem("pair", "Block size (Bytes): ", "" + info["size"]), elem("pair", "Page: ", "" + page), elem("pair", "Pages: ", "" + pages), elem("input", "Jump", "", function(input) {
          return askAnotherPage(type, jobid, input != null ? input.value : void 0);
        })
      ]
    };
    return _mapper.parseMapForParent(menuElem);
  };

  preContent = function(content) {
    var contentElem;
    contentElem = {
      type: "pre",
      cls: "code-container",
      title: content
    };
    return _mapper.parseMapForParent(contentElem);
  };

  params = _util.windowParameters();

  type = params["type"];

  jobid = params["jobid"];

  page = "1";

  askAnotherPage = function(type, jobid, page) {
    var msg;
    if (type && jobid) {
      return _logapi.readFromStart(jobid, type, page, function() {
        jobLogsElem.innerHTML = "";
        jobDetailsElem.innerHTML = "";
        return jobLinkElem.href = "/";
      }, function(ok, json) {
        var block, content, details, jobName, msg, result;
        result = null;
        if (ok) {
          content = json["content"];
          jobid = content["jobid"];
          jobName = content["jobname"];
          block = content["block"];
          jobLinkElem.href = "/job?jobid=" + jobid;
          details = {
            type: "div",
            children: [
              {
                type: "span",
                title: "" + jobName
              }, {
                type: "span",
                cls: "text-mute",
                title: "@" + jobid
              }
            ]
          };
          _mapper.parseMapForParent(details, jobDetailsElem);
          _mapper.parseMapForParent(menu(content), jobLogsElem);
          _mapper.parseMapForParent(preContent(block), jobLogsElem);
        } else {
          jobLinkElem.href = "/job?jobid=" + jobid;
          msg = json ? json["content"]["msg"] : "We know and keep working on that";
          result = _misc.blankslateWithMsg("Something went wrong :(", msg);
        }
        return _mapper.parseMapForParent(result, jobLogsElem);
      });
    } else {
      msg = _misc.blankslateWithMsg("Something went wrong :(", "Insufficient parameters, required type of logs and job id");
      return _mapper.parseMapForParent(msg, jobLogsElem);
    }
  };

  askAnotherPage(type, jobid, page);

}).call(this);
