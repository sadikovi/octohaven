jobHistory = document.getElementById("octohaven-jobs-history")
unless jobHistory
    throw new Error("Job history element could not be found")

_util = @util
_mapper = @mapper
_loader = @loader
_jobloader = new @JobLoader

# job statuses
[ALL, CREATED, FINISHED, WAITING, CLOSED, DELAYED] =
    ["ALL", "CREATED", "FINISHED", "WAITING", "CLOSED", "DELAYED"]

################################################################
# Request all jobs from the server
################################################################

blankslate = (internal) ->
    blankview = _mapper.parseMapForParent(type: "div", cls: "blankslate")
    _mapper.parseMapForParent(internal, blankview)
    blankview

blankslateWithMsg = (header, msg) ->
    header = type: "h1", cls: "text-thin", title: "#{header}"
    body = type: "p", title: "#{msg}"
    blankslate([header, body])

statusColumn = (status, colour, islarge=false) ->
    updatedClass = if islarge then "one-fourth column" else "one-eigth column"
    statusText = type: "span", cls: "#{colour}", title: "#{status}"
    statusSection = type: "div", cls: "section", children: statusText
    statusElem = type: "div", cls: "breadcrumb", children: statusSection
    elem = type: "div", cls: "#{updatedClass}", children: statusElem
    _mapper.parseMapForParent(elem)

buttonColumn = (btnTitle, action, islarge=false) ->
    updatedClass = if islarge then "one-fourth column" else "one-eigth column"
    btn = type: "div", cls: "btn btn-compact", title: "#{btnTitle}", onclick: (e) -> action?(this)
    elem = type: "div", cls: "#{updatedClass}", children: btn
    _mapper.parseMapForParent(elem)

jobColumn = (name, link, prefix, timestamp) ->
    column = "three-fourths column"
    # job section
    jobLink = type: "a", href: "#{link}", title: "#{name}"
    jobSuffix = type: "span", cls: "text-mute", title: "@Spark"
    jobSection = type: "div", cls: "section", children: [jobLink, jobSuffix]
    # time section
    timePrefix = type: "span", cls: "text-mute", title: "#{prefix}"
    datetime = type: "span", title: "#{_util.humanReadableTime(timestamp)}"
    timeSection = type: "div", cls: "section", children: [timePrefix, datetime]
    # closing breadcrumb
    job = type: "div", cls: "breadcrumb", children: [jobSection, timeSection]
    # column
    elem = type: "div", cls: "#{column}", children: job
    _mapper.parseMapForParent(elem)

statusColour = (status) ->
    return "text-blue" if (status == FINISHED)
    return "text-green" if (status == CREATED)
    return "text-yellow" if (status == WAITING)
    return "text-red" if (status == CLOSED)
    return "text-mute"

row = (jobObj) ->
    uid = jobObj["uid"]
    # submit time is in milliseconds
    submittime = jobObj["createtime"]
    status = jobObj["status"]
    name = jobObj["sparkjob"]["name"]
    # build columns
    jobCol = jobColumn(name, "/job?jobid=#{uid}", "Created ", submittime)
    showClose = status in [CREATED, DELAYED, WAITING]
    statusCol = statusColumn(status, statusColour(status), !showClose)
    buttonCol = buttonColumn("Close", (e) ->
        e.uid ?= uid
        fetch = =>
            _util.addClass(e, "btn-disabled")
            e.innerHTML = "???"
        update = (ok) =>
            _util.addClass(e, "btn-disabled")
            e.innerHTML = if ok then "Closed" else "Error"
        # fire api request to close this job
        _jobloader.close(e.uid, (-> fetch()), ((ok, json) -> update(ok)))
    )
    columns = type: "div", cls: "columns", children:
        [jobCol, statusCol, if showClose then buttonCol else null]
    segment = type: "div", cls: "segment", children: columns
    _mapper.parseMapForParent(segment)

reloadJobs = (status, limit = 30) ->
    # perform api call to fetch jobs
    _jobloader.get(status, limit
    , ->
        jobHistory.innerHTML = ""
    , (ok, json) ->
        if ok and json
            # load jobs
            jobs = json["content"]["jobs"]
            if jobs.length > 0
                # build rows and display jobs
                rows = [row(job) for job in jobs]
                segment = type: "div", cls: "segments", children: rows
                _mapper.parseMapForParent(segment, jobHistory)
            else
                # show blankview with a link to create a job
                header = type: "h1", cls: "text-thin", title: "No jobs found :("
                link = type: "a", href: "/create", title: "create a new job"
                text = type: "p", title: "You can ", children: link
                _mapper.parseMapForParent(blankslate([header, text]), jobHistory)
        else
            msg = if json then "#{json["content"]["msg"]}" else "We do not know what happened :("
            header = "Something went wrong"
            _mapper.parseMapForParent(blankslateWithMsg(header, msg), jobHistory)
    )

# add actions to different menu items
all = document.getElementById("octohaven-jobs-all")
created = document.getElementById("octohaven-jobs-created")
waiting = document.getElementById("octohaven-jobs-waiting")
delayed = document.getElementById("octohaven-jobs-delayed")
finished = document.getElementById("octohaven-jobs-finished")
closed = document.getElementById("octohaven-jobs-closed")

resetLabels = ->
    _util.removeClass(all, "selected")
    _util.removeClass(created, "selected")
    _util.removeClass(waiting, "selected")
    _util.removeClass(delayed, "selected")
    _util.removeClass(finished, "selected")
    _util.removeClass(closed, "selected")

selectLabel = (elem) ->
    _util.addClass(elem, "selected")

actionLabel = (e, elem, label) ->
    resetLabels()
    selectLabel(elem)
    reloadJobs?(label)
    e?.preventDefault()
    e?.stopPropagation()

_util.addEventListener(all, "click", (e) -> actionLabel(e, all, ALL))
_util.addEventListener(created, "click", (e) -> actionLabel(e, created, CREATED))
_util.addEventListener(waiting, "click", (e) -> actionLabel(e, waiting, WAITING))
_util.addEventListener(delayed, "click", (e) -> actionLabel(e, delayed, DELAYED))
_util.addEventListener(finished, "click", (e) -> actionLabel(e, finished, FINISHED))
_util.addEventListener(closed, "click", (e) -> actionLabel(e, closed, CLOSED))

# request all statuses
actionLabel(null, all, ALL)
