# job details
jobLinkElem = document.getElementById("octohaven-job-link")
jobDetailsElem = document.getElementById("octohaven-job-details")
jobLogsElem = document.getElementById("octohaven-job-logs")
unless jobDetailsElem and jobLogsElem and jobLinkElem
    throw new Error("Job detail and log elements are not found")

_mapper = @mapper
_util = @util
_jobloader = new @JobLoader

blankslate = (internal) ->
    blankview = _mapper.parseMapForParent(type: "div", cls: "blankslate")
    _mapper.parseMapForParent(internal, blankview)
    blankview

blankslateWithMsg = (header, msg) ->
    header = type: "h1", cls: "text-thin", title: "#{header}"
    body = type: "p", title: "#{msg}"
    blankslate([header, body])

elem = (type, args...) ->
    if type == "btn"
        # process button arguments
        type: "div", cls: "section", children: [
            type: "div", cls: "btn #{args[1]}", title: "#{args[0]}", onclick: args[2]
        ]
    else if type == "pair"
        # process pair arguments
        type: "div", cls: "section", children: [
            {type: "span", cls: "text-mute", title: "#{args[0]}"},
            {type: "span", title: "#{args[1]}"}
        ]
    else
        null

menu = (info) ->
    page = info["page"]
    pages = info["pages"]
    next = page + 1
    prev = page - 1
    btnCls = (page) -> if page < 0 or page >= pages then "btn-disabled" else ""
    # prepare menu
    menuElem = type: "div", cls: "breadcrumb", children: [
        # display two buttons and info
        elem("btn", "Prev", "#{btnCls(prev)}", action = () -> askAnotherPage(type, jobid, prev))
        elem("btn", "Next", "#{btnCls(next)}", action = () -> askAnotherPage(type, jobid, next))
        elem("pair", "Block size (Bytes): ", "#{info["size"]}")
        elem("pair", "Page: ", "#{page}"),
        elem("pair", "Pages: ", "#{pages}"),
    ]
    _mapper.parseMapForParent(menuElem)

preContent = (content) ->
    contentElem = type: "pre", cls: "code-container", title: content
    _mapper.parseMapForParent(contentElem)

# extract jobid from url
params = _util.windowParameters()
type = params["type"]
jobid = params["jobid"]
page = "0"

askAnotherPage = (type, jobid, page) ->
    if type and jobid
        logReader = new LogReader
        logReader.readFromStart(jobid, type, page, ->
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
                msg = if json then json["content"]["msg"] else "We know and keep working on that"
                result = blankslateWithMsg("Something went wrong :(",  msg)
            _mapper.parseMapForParent(result, jobLogsElem)
        )
    else
        # insufficient parameters
        msg = blankslateWithMsg("Something went wrong :(",
            "Insufficient parameters, required type of logs and job id")
        _mapper.parseMapForParent(msg, jobLogsElem)
# reload first page
askAnotherPage(type, jobid, page)
