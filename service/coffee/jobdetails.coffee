# job details
jobDetailsElem = document.getElementById("octohaven-job-details")
throw new Error("Job details element is not found") unless jobDetailsElem

_mapper = @mapper
_util = @util
_misc = @misc
_jobapi = new @JobApi

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

updateLogLinks = (uid) ->
    # update log links - stderr and stdout - to have uid
    stdout = document.getElementById("octohaven-job-stdout")
    stderr = document.getElementById("octohaven-job-stderr")
    stdout.href = "/log?type=stdout&jobid=#{uid}" if stdout
    stderr.href = "/log?type=stderr&jobid=#{uid}" if stderr

updateScheduleLink = (uid) ->
    # update link to create timetable for the job
    timetable = document.getElementById("octohaven-job-timetable")
    timetable.href = "/timetablecreate?id=#{uid}&mode=create" if timetable

# extract jobid from url
params = _util.windowParameters()
if "jobid" of params
    # extract jobid
    jobid = params["jobid"]
    _jobapi.getJob(jobid
        , ->
            jobDetailsElem.innerHTML = ""
        , (ok, json) ->
            if ok
                job = json["content"]["job"]
                uid = job["uid"]
                name = job["sparkjob"]["name"]
                status = job["status"]
                entrypoint = job["sparkjob"]["entrypoint"]
                masterurl = job["sparkjob"]["masterurl"]
                options = ("#{x} = #{y}" for x, y of job["sparkjob"]["options"])
                jobconf = ("#{x}" for x in job["sparkjob"]["jobconf"])
                jar = job["sparkjob"]["jar"]
                create = job["createtime"]
                submit = job["submittime"]
                sparkAppId = if job["sparkappid"] then job["sparkappid"] else "None"

                # build rows
                rowsElem = type: "div", cls: "segments", children: [
                    row(property(
                        column(contentHeader("Job id"), false),
                        column(contentValue(uid), true)
                    )),
                    row(property(
                        column(contentHeader("Spark job name"), false),
                        column(contentValue(name), true)
                    )),
                    row(property(
                        column(contentHeader("Created"), false),
                        column(type: "span", title: "#{_util.timestampToDate(create)}", true)
                    )),
                    row(property(
                        column(contentHeader("Expected run"), false),
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
                        column(contentHeader("Spark App Id"), false),
                        column(contentValue(sparkAppId), true)
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

                # update links for job logs
                updateLogLinks(uid)
                # update link for scheduling
                updateScheduleLink(uid)
            else
                msg = if json then json["content"]["msg"] else "We know and keep working on that"
                view = _misc.blankslateWithMsg("Something went wrong", msg)
                _mapper.parseMapForParent(view, jobDetailsElem)
    )
else
    jobDetailsElem.innerHTML = ""
    view = _misc.blankslateWithMsg("Something went wrong", "We know and keep working on that")
    _mapper.parseMapForParent(view, jobDetailsElem)
