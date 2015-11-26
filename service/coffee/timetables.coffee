timetablesElem = document.getElementById("octohaven-timetables")
throw new Error("Timetable placeholder is not found") unless timetablesElem

_mapper = @mapper
_util = @util
_misc = @misc
_timetableLoader = new @TimetableLoader

columnName = (name, uid, isactive) ->
    # status of timetable
    statusMsg = if isactive then "[ Active ]" else "[ Canceled ]"
    statusKlass = if isactive then "text-green" else "text-red"
    status = type: "span", cls: "#{statusKlass}", title: "#{statusMsg}"
    # name and link
    head = type: "a", href: "/timetable?id=#{uid}&mode=show", title: "#{name}"
    # overall parent structure
    breadcrumb = type: "div", cls: "breadcrumb", children: [
        _misc.section(status), _misc.section(head)]
    col = type: "div", cls: "two-fifths column", children: breadcrumb
    _mapper.parseMapForParent(col)

# statistics for timetable: run jobs, lost jobs, total number of jobs
columnStats = (run, lost, total) ->
    run = [{type: "span", title: "#{run}"}, {type: "span", cls: "text-mute", title: " run"}]
    lost = [{type: "span", title: "#{lost}"}, {type: "span", cls: "text-mute", title: " lost"}]
    total = [{type: "span", title: "#{total}"}, {type: "span", cls: "text-mute", title: " total"}]
    # overall parent structure
    breadcrumb = type: "div", cls: "breadcrumb", children: [
        _misc.section(run), _misc.section(lost), _misc.section(total)]
    col = type: "div", cls: "two-fifths column", children: breadcrumb
    _mapper.parseMapForParent(col)

columnControl = (uid, isactive, func) ->
    btn = if isactive then {type: "div", cls: "btn btn-compact", title: "Cancel"
        , onclick: (e) -> func?(@)} else null
    btn = _mapper.parseMapForParent(btn)
    btn.uid = uid
    col = type: "div", cls: "one-fifth column", children: btn
    _mapper.parseMapForParent(col)

row = (obj) ->
    name = obj["name"]
    uid = obj["uid"]
    run = _util.intOrElse(obj["numjobs"], -1)
    total = _util.intOrElse(obj["numtotaljobs"], -1)
    lost = total - run
    isactive = !obj["canceled"]
    colName = columnName(name, uid, isactive)
    colStats = columnStats(run, lost, total)
    colControl = columnControl(uid, isactive, (obj) ->
        fetch = =>
            _util.addClass(obj, "btn-disabled")
            obj.innerHTML = "???"
        update = (ok) =>
            _util.addClass(obj, "btn-disabled")
            obj.innerHTML = if ok then "Canceled" else "Error"
        _timetableLoader.cancel(obj.uid, (-> fetch()), ((ok, json) -> update(ok)))
    )
    _misc.segment(_misc.columns([colName, colStats, colControl]))

update = ->
    _timetableLoader.list(false, ->
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

# update timetables
update?()
