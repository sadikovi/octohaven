timetableCreateElem = document.getElementById("octohaven-timetable-create")
cronHelpElem = document.getElementById("octohaven-cron-help")
unless timetableCreateElem and cronHelpElem
    throw new Error("Timetable placeholders are not found")

_mapper = @mapper
_util = @util
_misc = @misc
_namer = @namer
_jobapi = new @JobApi
_timetableApi = new @TimetableApi

# extract parameters from window
params = _util.windowParameters()
mode = params?.mode
id = params?.id

# mode check
unless mode == "create"
    view = _misc.blankslateWithMsg("Something went wrong :(", "Unrecognized mode")
    _mapper.parseMapForParent(view, timetableCreateElem)
    return
# id check
unless id
    view = _misc.blankslateWithMsg("Something went wrong :(", "Undefined id")
    _mapper.parseMapForParent(view, timetableCreateElem)
    return

# submit button and global status bar
controlBar = document.getElementById("octohaven-create-controls")
submitBtn = document.getElementById("octohaven-submit-timetable")
statusBar = document.getElementById("octohaven-validation-status")
throw new Error("Submit requirements failed") unless controlBar and statusBar and submitBtn
# job submission status (does not allow to resubmit already sent job)
IS_SUBMITTED = false

# default timetable to load
DEFAULT_TIMETABLE = new @Timetable({
    "name": "Timetable #{_namer.generate()}",
    "pattern": "",
    "jobid": ""
    "jobname": "Undefined"
})
currentTimetable = DEFAULT_TIMETABLE

################################################################
# Submit and status methods
################################################################
setLoadStatus = (load) ->
    if load then _util.addClass(statusBar, "loading") else _util.removeClass(statusBar, "loading")

setSubmitStatus = (ok, internal) ->
    statusBar.innerHTML = ""
    mode = if ok then "success-box" else "error-box"
    obj = type: "div", cls: mode, children: internal
    _mapper.parseMapForParent(obj, statusBar)

setTextStatus = (ok, text) -> setSubmitStatus(ok, type: "span", title: "#{text}")

submitTimetable = (timetable) ->
    setLoadStatus(true)
    unless IS_SUBMITTED
        IS_SUBMITTED = true
        # extracting latest changes from the current timetable
        settings = timetable.settings
        _timetableApi.submit settings, null, (ok, content) ->
            setLoadStatus(false)
            if ok
                msg = content["content"]["msg"]
                uid = content["content"]["uid"]
                body = type: "span", title: "#{msg}. ", children:
                    type: "a", title: "View details", href: "/timetable?id=#{uid}&mode=show"
                setSubmitStatus(ok, body)
            else
                IS_SUBMITTED = false
                msg = if content then content["content"]["msg"] else "Something went wrong :("
                setTextStatus(ok, msg)
    else
        setTextStatus(false, "You cannot resubmit the timetable")
        setLoadStatus(false)

################################################################
# Mode resolution and building web page
################################################################
# init submit button
_util.addEventListener submitBtn, "click", (e) ->
    submitTimetable(currentTimetable)
    e.preventDefault()
    e.stopPropagation()
# load clone job
_jobapi.getJob(id, ->
    timetableCreateElem.innerHTML = ""
, (ok, json) ->
    result = null
    if ok
        # show controls and status bar, since we loaded job
        _util.removeClass(controlBar, "hidden")
        _util.removeClass(statusBar, "hidden")
        _util.removeClass(cronHelpElem, "hidden")

        job = json["content"]["job"]
        jobid = job["uid"]
        jobname = job["sparkjob"]["name"]
        currentTimetable.set("jobid", jobid)
        currentTimetable.set("jobname", jobname)
        rows = [
            _misc.staticOption("Clone job", "Base job for timetable",
                {type: "a", href: "/job?jobid=#{jobid}", title: "#{jobname}"})
            _misc.dynamicOption("Name", "Timetable name", "#{currentTimetable.get("name")}"
                , (status, value) -> currentTimetable.set("name", value) if status),
            _misc.dynamicOption("Cron pattern", "Cron expression for scheduling",
                "#{currentTimetable.get("pattern")}", (status, value) ->
                    currentTimetable.set("pattern", value) if status)
        ]
        result = _misc.segments(rows)
    else
        msg = if json then json["content"]["msg"] else "We know and keep working on that"
        result = _misc.blankslateWithMsg("Something went wrong :(",  msg)
    _mapper.parseMapForParent(result, timetableCreateElem)
)
