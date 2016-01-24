# job details
jobLinkElem = document.getElementById("octohaven-job-link")
jobDetailsElem = document.getElementById("octohaven-job-details")
jobLogsElem = document.getElementById("octohaven-job-logs")
unless jobDetailsElem and jobLogsElem and jobLinkElem
    throw new Error("Job detail and log elements are not found")

_mapper = @mapper
_util = @util
_misc = @misc
_jobapi = new @JobApi
_logapi = new @LogApi

elem = (type, args...) ->
    if type == "btn"
        # process button arguments
        _misc.section([type: "div", cls: "btn #{args[1]}", title: "#{args[0]}", onclick: args[2]])
    else if type == "pair"
        # process pair arguments
        _misc.section([{type: "span", cls: "text-mute", title: "#{args[0]}"},
            {type: "span", title: "#{args[1]}"}])
    else if type == "input"
        # add input box and button with action
        input = _mapper.parseMapForParent({type: "input", inputtype: "text", cls: "input-squared"
            , inputvalue: "#{args[1]}"})
        action = args[2]
        btn = _mapper.parseMapForParent({type: "div", cls: "btn tooltipped tooltipped-n"
            ,title: "#{args[0]}", arialabel: "Jump to the page", onclick: () ->
                action?(this.input)})
        btn.input = input
        _misc.section([input, {type: "div", cls: "separator"}, btn])
    else
        null

menu = (info) ->
    page = info["page"]
    pages = info["pages"]
    next = page + 1
    prev = page - 1
    btnCls = (page) -> if page < 1 or page > pages then "btn-disabled" else ""
    # prepare menu
    menuElem = type: "div", cls: "breadcrumb", children: [
        # display two buttons and info
        elem("btn", "Prev", "#{btnCls(prev)}", action = () -> askAnotherPage(type, jobid, prev))
        elem("btn", "Next", "#{btnCls(next)}", action = () -> askAnotherPage(type, jobid, next))
        elem("btn", "Last", "", action = () -> askAnotherPage(type, jobid, pages))
        elem("pair", "Block size (Bytes): ", "#{info["size"]}")
        elem("pair", "Page: ", "#{page}")
        elem("pair", "Pages: ", "#{pages}")
        elem("input", "Jump", "", (input) -> askAnotherPage(type, jobid, input?.value))
    ]
    _mapper.parseMapForParent(menuElem)

preContent = (content) ->
    contentElem = type: "pre", cls: "code-container", title: content
    _mapper.parseMapForParent(contentElem)

# extract jobid from url
params = _util.windowParameters()
type = params["type"]
jobid = params["jobid"]
page = "1"

askAnotherPage = (type, jobid, page) ->
    if type and jobid
        _logapi.readFromStart(jobid, type, page, ->
            jobLogsElem.innerHTML = ""
            jobDetailsElem.innerHTML = ""
            jobLinkElem.href = "/"
        , (ok, json) ->
            result = null
            if ok
                # display log nicely
                content = json["content"]
                jobid = content["jobid"]
                jobName = content["jobname"]
                block = content["block"]
                # update job back link
                jobLinkElem.href = "/job?jobid=#{jobid}"
                # update job details
                details = type: "div", children: [
                    {type: "span", title: "#{jobName}"},
                    {type: "span", cls: "text-mute", title: "@#{jobid}"}
                ]
                _mapper.parseMapForParent(details, jobDetailsElem)
                # update log details
                _mapper.parseMapForParent(menu(content), jobLogsElem)
                _mapper.parseMapForParent(preContent(block), jobLogsElem)
            else
                # we update job back link even in case if something has failed, we still want to
                # use previous job id to go back to the details.
                jobLinkElem.href = "/job?jobid=#{jobid}"
                msg = if json then json["content"]["msg"] else "We know and keep working on that"
                result = _misc.blankslateWithMsg("Something went wrong :(",  msg)
            _mapper.parseMapForParent(result, jobLogsElem)
        )
    else
        # insufficient parameters
        msg = _misc.blankslateWithMsg("Something went wrong :(",
            "Insufficient parameters, required type of logs and job id")
        _mapper.parseMapForParent(msg, jobLogsElem)
# reload first page
askAnotherPage(type, jobid, page)
