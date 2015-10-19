# job details
jobDetailsElem = document.getElementById("octohaven-job-details")
throw new Error("Job details element is not found") unless jobDetailsElem

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

contentHeader = (value) -> type: "span", cls: "text-mute", title: "#{value}"

contentValue = (value) -> type: "span", title: "#{value}"

contentList = (list) -> (type: "p", children: type: "span", title: "#{x}" for x in list)

column = (content, islarge=false) ->
    updatedClass = if islarge then "four-fifths column" else "one-fifth column"
    col = type: "div", cls: "#{updatedClass}", children: content
    _mapper.parseMapForParent(col)

property = (cols...) ->
    prop = type: "div", cls: "columns", children: [x for x in cols]
    _mapper.parseMapForParent(prop)

row = (property) ->
    rw = type: "div", cls: "segment", children: property
    _mapper.parseMapForParent(rw)

# extract jobid from url
unless window.location and window.location.search
    throw new Error("Window.location is not set properly")
searchstr = window.location.search?.trim().split("=")
if _util.isArray(searchstr) and searchstr.length == 2
    # extract jobid
    jobid = searchstr[1]
    _jobloader.getJob(jobid
        , ->
            jobDetailsElem.innerHTML = ""
        , (ok, json) ->
            if ok
                job = json["content"]["job"]
                name = job["sparkjob"]["name"]
                status = job["status"]
                entrypoint = job["sparkjob"]["entrypoint"]
                masterurl = job["sparkjob"]["masterurl"]
                options = ("#{x} = #{y}" for x, y of job["sparkjob"]["options"])
                jobconf = ("#{x}" for x in job["sparkjob"]["jobconf"])
                jar = job["sparkjob"]["jar"]
                submit = job["submittime"]

                # build rows
                rowsElem = type: "div", cls: "segments", children: [
                    row(property(
                        column(contentHeader("Spark job name"), false),
                        column(contentValue(name), true)
                    )),
                    row(property(
                        column(contentHeader("Created"), false),
                        column(type: "span", title: "#{_util.timestampToDate(submit)}", true)
                    )),
                    row(property(
                        column(contentHeader("Status"), false),
                        column(contentValue(status), true)
                    )),
                    row(property(column(
                        contentHeader("Entrypoint"), false),
                        column(contentValue(entrypoint), true)
                    )),
                    row(property(
                        column(contentHeader("Spark URL"), false),
                        column(contentValue(masterurl), true)
                    )),
                    row(property(
                        column(contentHeader("Jar file"), false),
                        column(contentValue(jar), true)
                    )),
                    row(property(
                        column(contentHeader("Options"), false),
                        column(contentList(options), true)
                    )),
                    row(property(
                        column(contentHeader("Job conf"), false),
                        column(contentList(jobconf), true)
                    ))
                ]
                _mapper.parseMapForParent(rowsElem, jobDetailsElem)
            else
                msg = if json then json["content"]["msg"] else "We know and keep working on that"
                view = blankslateWithMsg("Something went wrong", msg)
                _mapper.parseMapForParent(view, jobDetailsElem)
    )
else
    jobDetailsElem.innerHTML = ""
    view = blankslateWithMsg("Something went wrong", "We know and keep working on that")
    _mapper.parseMapForParent(view, jobDetailsElem)
