timetablesElem = document.getElementById("octohaven-timetables")
throw new Error("Timetable placeholder is not found") unless timetablesElem

_mapper = @mapper
_util = @util
_misc = @misc
_timetableLoader = new @TimetableLoader
# statuses
[ACTIVE, PAUSED, CANCELED] = ["ACTIVE", "PAUSED", "CANCELED"]

column = (size, content, parent=null) ->
    brd = type: "div", cls: "breadcrumb", children: content
    col = type: "div", cls: "#{size} column", children: brd
    _mapper.parseMapForParent(col, parent)

statusColour = (status) ->
    return "text-green" if status == ACTIVE
    return "text-yellow" if status == PAUSED
    return "text-red" if status == CANCELED
    return "text-mute"

actionName = (status) ->
    return "Pause" if status == ACTIVE
    return "Resume" if status == PAUSED
    return null

columnStatus = (status, colour) ->
    st = type: "div", cls: "#{colour}", title: "#{status}"
    section = type: "div", cls: "section", children: st
    column("one-sixth", section)

columnName = (uid, name) ->
    nm = type: "a", href: "/timetable?id=#{uid}&mode=show", title: "#{name}"
    section = type: "div", cls: "section", children: nm
    column("one-third", section)

columnStats = (numJobs, jobid, timestamp) ->
    # counter and text
    counter = type: "span", title: "#{numJobs}"
    countertext = type: "span", cls: "text-mute", title: " scheduled jobs"
    section1 = type: "div", cls: "section", children: [counter, countertext]
    # timestamp and jobid of latest run
    section2 = null
    if timestamp and timestamp > 0
        jobid = type: "a", href: "/job?jobid=#{jobid}", title: "latest "
        time = type: "span", title: "#{_util.timestampToDate(timestamp)}"
        section2 = type: "div", cls: "section", children: [jobid, time]
    column("one-third", [section1, section2])

columnAction = (uid, name, status, action) ->
    btn = type: "div", cls: "btn btn-compact", title: "#{name}", onclick: ->
        @uid = uid
        @status = status
        action?(@)
    section = type: "div", cls: "section", children: btn
    column("one-sixth", section)

row = (obj) ->
    uid = obj["uid"]
    name = obj["name"]
    numJobs = obj["numjobs"]
    status = obj["status"]
    jobid = obj["latestrunjobid"]
    timestamp = obj["latestruntime"]
    # build columns
    colStatus = columnStatus(status, statusColour(status))
    colName = columnName(uid, name)
    colStats = columnStats(numJobs, jobid, timestamp)
    colAction = null
    aname = actionName(status)
    if aname
        colAction = columnAction(uid, aname, status, (obj) ->
            fetch = =>
                _util.addClass(obj, "btn-disabled")
                obj.innerHTML = "???"
            update = (ok) =>
                _util.addClass(obj, "btn-disabled")
                if ok
                    obj.innerHTML = if obj.status == ACTIVE then "Paused" else "Active"
                else
                    obj.innerHTML = "Error"
            if obj.status == ACTIVE
                _timetableLoader.pause(obj.uid, (-> fetch()), ((ok, json) -> update(ok)))
            else if obj.status == PAUSED
                _timetableLoader.resume(obj.uid, (-> fetch()), ((ok, json) -> update(ok)))
        )
    _misc.segment(_misc.columns([colStatus, colName, colStats, colAction]))

update = (statuses) ->
    console.log statuses
    _timetableLoader.list(false, statuses, ->
        timetablesElem.innerHTML = ""
    , (ok, json) ->
        if ok
            timetables = json["content"]["timetables"]
            if timetables and timetables.length > 0
                rows = [row(timetable) for timetable in timetables]
                _misc.segments(rows, timetablesElem)
            else
                view = _misc.blankslateWithMsg("No timetables found :(",
                    "You can still create a timetable for any job from job view")
                _mapper.parseMapForParent(view, timetablesElem)
        else
            msg = if json then json["content"]["msg"] else "We know and keep working on that"
            result = _misc.blankslateWithMsg("Something went wrong :(", msg)
            _mapper.parseMapForParent(result, timetablesElem)
    )

# add actions to different menu items
noncanceled = document.getElementById("octohaven-timetables-noncanceled")
active = document.getElementById("octohaven-timetables-active")
paused = document.getElementById("octohaven-timetable-paused")
canceled = document.getElementById("octohaven-timetable-canceled")

resetLabels = ->
    _util.removeClass(noncanceled, "selected")
    _util.removeClass(active, "selected")
    _util.removeClass(paused, "selected")
    _util.removeClass(canceled, "selected")

selectLabel = (elem) ->
    _util.addClass(elem, "selected")

actionLabel = (e, elem, statuses) ->
    resetLabels()
    update?(statuses)
    selectLabel(elem)
    e?.preventDefault()
    e?.stopPropagation()

_util.addEventListener(noncanceled, "click", (e) -> actionLabel(e, noncanceled, [ACTIVE, PAUSED]))
_util.addEventListener(active, "click", (e) -> actionLabel(e, active, [ACTIVE]))
_util.addEventListener(paused, "click", (e) -> actionLabel(e, paused, [PAUSED]))
_util.addEventListener(canceled, "click", (e) -> actionLabel(e, canceled, [CANCELED]))

# request non canceled statuses, update timetables
actionLabel(null, noncanceled, [ACTIVE, PAUSED])
