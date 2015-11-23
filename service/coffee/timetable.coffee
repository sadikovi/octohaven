headerElem = document.getElementById("octohaven-timetable-header")
timetableShowElem = document.getElementById("octohaven-timetable-show")
timetableCreateElem = document.getElementById("octohaven-timetable-create")
timetableIntervalsElem = document.getElementById("octohaven-timetable-create-intervals")
timetableCreateParamsElem = document.getElementById("octohaven-timetable-create-params")
unless headerElem and timetableShowElem and timetableCreateElem and timetableIntervalsElem
    throw new Error("Timetable placeholders are not found")

_mapper = @mapper
_util = @util
_misc = @misc
_timetableLoader = new @TimetableLoader
_jobLoader = new @JobLoader

# extract parameters from window
params = _util.windowParameters()
mode = params?.mode
id = params?.id
# mode check
unless mode == "show" or mode == "create"
    _util.removeClass(timetableShowElem, "hidden")
    view = _misc.blankslateWithMsg("Something went wrong :(", "Unrecognized mode")
    _mapper.parseMapForParent(view, timetableShowElem)
    return
# id check
if id == null
    _util.removeClass(timetableShowElem, "hidden")
    view = _misc.blankslateWithMsg("Something went wrong :(", "Undefined id")
    _mapper.parseMapForParent(view, timetableShowElem)
    return

# resolve header
if mode == "show"
    headerElem.innerHTML = "View timetable"
else if mode == "create"
    headerElem.innerHTML = "Create new timetable"
else
    headerElem.innerHTML = ""

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

intervalEntry = (name, interval, parent) ->
    elemMap = type: "a", cls: "menu-item", title: "#{name}", href: ""
    elem = _mapper.parseMapForParent(elemMap, parent)
    elem.interval = interval
    elem

intervalMenu = ->
    menu = _mapper.parseMapForParent({type: "nav", cls: "menu"})
    delays = {
        600: intervalEntry("Every 10 minutes", 10*60, menu),
        3600: intervalEntry("Every 1 hour", 1*60*60, menu),
        10800: intervalEntry("Every 3 hours", 3*60*60, menu),
        86400: intervalEntry("Every day", 24*60*60, menu),
        259200: intervalEntry("Every 3 days", 3*24*60*60, menu)
    }
    menu

# create different templates for each mode
if mode == "show"
    # show mode
    _timetableLoader.get(id, ->
        timetableShowElem.innerHTML = ""
        _util.removeClass(timetableShowElem, "hidden")
        _util.addClass(timetableCreateParamsElem, "hidden")
        _util.addClass(timetableCreateElem, "hidden")
        _util.addClass(timetableIntervalsElem, "hidden")
    , (ok, json) ->
        result = null
        if ok
            timetable = json["content"]["timetable"]
            job = json["content"]["job"]
            jobid = job["uid"]
            jobname = job["sparkjob"]["name"]
            rows = [
                keyValue("Name", "Timetable name", timetable["name"]),
                keyValue("Status", "Whether jobs keep running under this schedule",
                    if timetable["canceled"] then "CANCELED" else "ACTIVE"),
                keyElem("Clone job", "Job that is used to create jobs for timetable",
                    {type: "a", href: "/job?jobid=#{jobid}", title: "#{jobname}"})
                keyValue("Start time", "Start time for timetable",
                    _util.timestampToDate(timetable["starttime"])),
                keyValue("Number of jobs run", "Number of actual jobs having run",
                    timetable["numjobs"]),
                keyValue("Total number of jobs", "Estimated total number of jobs",
                    timetable["numtotaljobs"]),
                keyValue("Intervals in sec", "Actual schedule for timetable",
                    timetable["intervals"])
            ]
            result = _misc.segments(rows)
        else
            msg = if json then json["content"]["msg"] else "We know and keep working on that"
            result = _misc.blankslateWithMsg("Something went wrong :(",  msg)
        _mapper.parseMapForParent(result, timetableShowElem)
    )
else if mode == "create"
    # create mode
    _jobLoader.getJob(id, ->
        timetableCreateElem.innerHTML = ""
        _util.removeClass(timetableCreateParamsElem, "hidden")
        _util.removeClass(timetableCreateElem, "hidden")
        _util.removeClass(timetableIntervalsElem, "hidden")
        _util.addClass(timetableShowElem, "hidden")
    , (ok, json) ->
        result = null
        if ok
            job = json["content"]["job"]
            jobid = job["uid"]
            jobname = job["sparkjob"]["name"]
            params = [
                keyElem("Base job for the timetable", "Job that is used to create jobs for timetable",
                    {type: "a", href: "/job?jobid=#{jobid}", title: "#{jobname}"})
            ]
            rows = [
                _misc.jobOption("Name", "Timetable name", "dummy", (status, value) ->
                    console.log status, value)
            ]

            result = _misc.segments(rows)
            _mapper.parseMapForParent(params, timetableCreateParamsElem)
            _mapper.parseMapForParent({type: "h4", title: "Choose interval"}
                , timetableIntervalsElem)
            _mapper.parseMapForParent(intervalMenu(), timetableIntervalsElem)
        else
            msg = if json then json["content"]["msg"] else "We know and keep working on that"
            result = _misc.blankslateWithMsg("Something went wrong :(",  msg)
        _mapper.parseMapForParent(result, timetableCreateElem)
    )
