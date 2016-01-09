timetableShowElem = document.getElementById("octohaven-timetable-show")
unless timetableShowElem
    throw new Error("Timetable placeholders are not found")

_mapper = @mapper
_util = @util
_misc = @misc
_timetableApi = new @TimetableApi

# extract parameters from window
params = _util.windowParameters()
mode = params?.mode
id = params?.id
# mode check
unless mode == "show"
    view = _misc.blankslateWithMsg("Something went wrong :(", "Unrecognized mode")
    _mapper.parseMapForParent(view, timetableShowElem)
    return
# id check
if id == null
    view = _misc.blankslateWithMsg("Something went wrong :(", "Undefined id")
    _mapper.parseMapForParent(view, timetableShowElem)
    return

# cancel button and global status bar
showControls = document.getElementById("octohaven-show-controls")
statusBar = document.getElementById("octohaven-validation-status")
cancelBtn = document.getElementById("octohaven-cancel-timetable")
throw new Error("Control requirements failed") unless showControls and cancelBtn and statusBar

################################################################
# Cancel and status methods
################################################################
setLoadStatus = (load) ->
    if load then _util.addClass(statusBar, "loading") else _util.removeClass(statusBar, "loading")

setSubmitStatus = (ok, internal) ->
    statusBar.innerHTML = ""
    mode = if ok then "success-box" else "error-box"
    obj = type: "div", cls: mode, children: internal
    _mapper.parseMapForParent(obj, statusBar)

setTextStatus = (ok, text) -> setSubmitStatus(ok, type: "span", title: "#{text}")

cancelTimetable = (uid) ->
    setLoadStatus(true)
    _timetableApi.cancel uid, null, (ok, content) ->
        setLoadStatus(false)
        msg = if content then content["content"]["msg"] else "Something went wrong :("
        setTextStatus(ok, msg)

################################################################
# Building blocks and util functions
################################################################
column = (width, content, parent = null) ->
    col = type: "div", cls: "#{width} column", children: content
    _mapper.parseMapForParent(col, parent)

keyElem = (key, desc, elem) ->
    keyElement = _mapper.parseMapForParent({type: "span", cls: "text-mute tooltipped tooltipped-n"
        , title: "#{key}"})
    keyElement.setAttribute("aria-label", "#{desc}")
    list = [
        column("one-fourth", keyElement),
        column("three-fourths", {type: "span", children: elem})
    ]
    _misc.segment(_misc.columns(list))

keyValue = (key, desc, value) -> keyElem(key, desc, {type: "span", title: "#{value}"})

timeToDate = (timestamp, alter) ->
    if timestamp > 0
        return _util.timestampToDate(timestamp)
    return "#{alter}"

################################################################
# Building web page
################################################################
# load timetable for uid
_timetableApi.get(id, ->
    timetableShowElem.innerHTML = ""
, (ok, json) ->
    result = null
    if ok
        # show status bar and controls
        _util.removeClass(statusBar, "hidden")
        _util.removeClass(showControls, "hidden")

        timetable = json["content"]["timetable"]
        job = json["content"]["job"]
        jobid = job["uid"]
        jobname = job["sparkjob"]["name"]
        rows = [
            keyValue("Timetable id", "Timetable id", timetable["uid"]),
            keyValue("Name", "Timetable name", timetable["name"]),
            keyValue("Status", "Timetable status", timetable["status"]),
            keyElem("Clone job", "Job that is used to create jobs for timetable",
                {type: "a", href: "/job?jobid=#{jobid}", title: "#{jobname}"}),
            keyValue("Cron expression", "Timetable schedule as Cron expression",
                timetable["crontab"]["pattern"]),
            keyValue("Start time", "Start time for timetable",
                timeToDate(timetable["starttime"], "None")),
            keyValue("Stop time", "Stop time for timetable (if cancelled)",
                timeToDate(timetable["stoptime"], "None")),
            keyValue("Number of jobs run", "Number of actual jobs having run",
                timetable["numjobs"])
            keyElem("Latest scheduled job", "Latest scheduled job for timetable",
                {type: "a", href: "/job?jobid=#{timetable.latestjobid}", title: "view"}),
            keyValue("Latest run", "Latest run (if any)",
                timeToDate(timetable["latestruntime"], "None"))
        ]
        result = _misc.segments(rows)

        # show cancel button
        if timetable["status"] == "CANCELLED"
            _util.addClass(cancelBtn, "btn-disabled")
        else
            cancelBtn.uid = timetable["uid"]
            _util.addEventListener cancelBtn, "click", (e) ->
                cancelTimetable(@uid)
                e.preventDefault()
                e.stopPropagation()
    else
        msg = if json then json["content"]["msg"] else "We know and keep working on that"
        result = _misc.blankslateWithMsg("Something went wrong :(",  msg)
    _mapper.parseMapForParent(result, timetableShowElem)
)
