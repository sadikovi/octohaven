# dependencies
_filelist = new @FilelistApi
_tempapi = new @TemplateApi
_jobapi = new @JobApi
_util = @util
_mapper = @mapper
_namer = @namer
_misc = @misc

# job settings elements
jobCanvas = document.getElementById("octohaven-job-settings")
throw new Error("Job settings canvas is undefined") unless jobCanvas
# file system elements
breadcrumbsElem = document.getElementById("octohaven-filelist-breadcrumbs")
filesElem = document.getElementById("octohaven-filelist-files")
selectedJarElem = document.getElementById("octohaven-selected-jar")
unless breadcrumbsElem and filesElem and selectedJarElem
    throw new Error("Cannot build file list")
# delay settings
delayElem = document.getElementById("octohaven-job-delay")
throw new Error("Cannot find delay element") unless delayElem
# template settings
templateHeading = document.getElementById("octohaven-templates")
templateButton = document.getElementById("octohaven-save-template")
throw new Error("Cannot find template elements") unless templateHeading and templateButton
# submit button and global status bar
submitBtn = document.getElementById("octohaven-submit-job")
statusBar = document.getElementById("octohaven-validation-status")
throw new Error("Submit requirements failed") unless submitBtn and statusBar
# job submission status (does not allow to resubmit already sent job)
IS_SUBMITTED = false
# default (start up) template to load
DEFAULT_TEMPLATE = new @Template({
    "name": _namer.generate(),
    "entrypoint": "org.test.Main",
    "driver-memory": "8g",
    "executor-memory": "8g",
    "options": "",
    "jobconf": "",
    "delay": "0"
    "jar": ""
})

################################################################
# Misc: display status
################################################################
setLoadStatus = (load) ->
    if load then _util.addClass(statusBar, "loading") else _util.removeClass(statusBar, "loading")

setSubmitStatus = (ok, internal) ->
    statusBar.innerHTML = ""
    mode = if ok then "success-box" else "error-box"
    obj = type: "div", cls: mode, children: internal
    _mapper.parseMapForParent(obj, statusBar)

setTextStatus = (ok, text) -> setSubmitStatus(ok, type: "span", title: "#{text}")

################################################################
# Display file finder
################################################################
ls = (name, cls, path, onClick) ->
    tp = if onClick then "a" else "div"
    elem = type: "#{tp}", cls: "#{cls}", title: "#{name}", onclick: (e) ->
        onClick?(@)
        e.preventDefault()
        e.stopPropagation()
    elem = _mapper.parseMapForParent(elem)
    elem.path = path
    return elem
# to keep track of last selected element with jar file
lastSelectedJarElem = null

# fetching breadcrumbs
breadcrumbs = (dir, func, eachElemFunc) ->
    _filelist.breadcrumbs(dir, ->
        breadcrumbsElem.innerHTML = ""
    , (ok, json) =>
        if ok
            [arr, parts] = [[], json["content"]["breadcrumbs"]]
            for obj, i in parts
                if i < parts.length-1
                    elem = ls(obj["name"], "section", obj["path"], (el) ->
                        if func?(el)
                            breadcrumbs(el.obj.path, func, eachElemFunc)
                            files(el.obj.path, func, eachElemFunc)
                    )
                    elem.obj = obj
                    eachElemFunc?(elem)
                    arr.push(elem)
                    arr.push(type: "div", cls: "separator", title: "/")
                else
                    elem = ls(obj["name"], "active section", obj["path"])
                    elem.obj = obj
                    eachElemFunc?(elem)
                    arr.push(elem)
            _mapper.parseMapForParent(arr, breadcrumbsElem)
        else if json
            setTextStatus(false, json["content"]["msg"])
        else
            setTextStatus(false, "Something went wrong :(")
    )

files = (dir, func, eachElemFunc) ->
    _filelist.files(dir, ->
        filesElem.innerHTML = ""
    , (ok, json) =>
        if ok
            [arr, parts] = [[], json["content"]["list"]]
            for obj in parts
                elem = type: "a", cls: "menu-item", href: "", title: "[#{obj.tp}] #{obj.name}"
                elem["onclick"] = (e) ->
                    if func?(@)
                        breadcrumbs(@obj.path, func, eachElemFunc)
                        files(@obj.path, func, eachElemFunc)
                    e.preventDefault()
                    e.stopPropagation()
                elem = _mapper.parseMapForParent(elem)
                elem.obj = obj
                eachElemFunc?(elem)
                arr.push(elem)
            _mapper.parseMapForParent(arr, filesElem)
        else if json
            setTextStatus(false, json["content"]["msg"])
        else
            setTextStatus(false, "Something went wrong :(")
    )

################################################################
# Delay settings
################################################################
# set delay settings, clean up parent element and update menu
delayElem.innerHTML = ""

delayEntry = (name, delay) ->
    elemMap = type: "a", cls: "menu-item", title: "#{name}", href: ""
    elem = _mapper.parseMapForParent(elemMap, delayElem)
    elem.diff = delay
    elem

delays = {
    0: delayEntry("Right away", 0),
    600: delayEntry("In 10 minutes", 10*60),
    1800: delayEntry("In 30 minutes", 30*60),
    3600: delayEntry("In 1 hour", 1*60*60),
    10800: delayEntry("In 3 hours", 3*60*60),
    86400: delayEntry("Next day", 24*60*60)
}

################################################################
# Loading template
################################################################
loadTemplate = (job) ->
    # 1. create options
    jobCanvas.innerHTML = ""
    # build table
    settings = [
        _misc.dynamicOption("Job name", "Friendly job name", job.get("name"),
            (ok, value) -> job.set("name", "#{value}") if ok)
        _misc.dynamicOption("Main class", "Entrypoint for the job", job.get("entrypoint"),
            (ok, value) -> job.set("entrypoint", "#{value}") if ok)
        _misc.dynamicOption("Driver memory", "Memory for the driver programme",
            job.get("driver-memory"), (ok, value) -> job.set("driver-memory", "#{value}") if ok)
        _misc.dynamicOption("Executor memory", "Memory for Spark executors",
            job.get("executor-memory"), (ok, value) -> job.set("executor-memory", "#{value}") if ok)
        _misc.dynamicOption("Spark options", "Settings, e.g. JVM, networking, shuffle...",
            job.get("options"), (ok, value) -> job.set("options", "#{value}") if ok)
        _misc.dynamicOption("Job options", "Job options to pass to entrypoint",
            job.get("jobconf"), (ok, value) -> job.set("jobconf", "#{value}") if ok)
    ]
    jobRows = _misc.segments(settings, jobCanvas)

    # 2. update jar file
    selectedJarElem.innerHTML = if job.get("jar") != "" then "#{job.get("jar")}" else "&nbsp;"
    traverse = (elem) ->
        if elem.obj.tp == "JAR"
            job.set("jar", "#{elem.obj.path}")
            selectedJarElem.innerHTML = job.get("jar")
            select(elem)
            return false
        return true
    select = (elem) ->
        file = elem.obj
        if file.tp == "JAR" and file.path == job.get("jar")
            if lastSelectedJarElem
                _util.removeClass(lastSelectedJarElem, "selected")
            _util.addClass(elem, "selected")
            lastSelectedJarElem = elem
    breadcrumbs("", traverse, select)
    files("", traverse, select)
    # 3. update delay options
    changeDelay = (delay) ->
        job?.set("delay", delay.diff)
        _util.removeClass(each, "selected") for key, each of delays
        _util.addClass(delay, "selected")
    loadDelay = (delay) ->
        diff = _util.intOrElse(delay, 0)
        delay = if diff of delays then delays[diff] else delays[0]
        changeDelay(delay)

    for key, value of delays
        _util.addEventListener value, "click", (e) ->
            changeDelay(@)
            e.preventDefault()
            e.stopPropagation()

    loadDelay(job.get("delay"))

################################################################
# Submit job
################################################################
submitJob = (job) ->
    setLoadStatus(true)
    unless IS_SUBMITTED
        IS_SUBMITTED = true
        # extracting latest changes from the current job
        settings = job.settings
        _jobapi.submit settings, null, (ok, content) ->
            setLoadStatus(false)
            if ok
                # extract job id
                msg = content["content"]["msg"]
                jobid = content["content"]["jobid"]
                body = type: "span", title: "#{msg}. ", children:
                    type: "a", title: "View details", href: "/job?jobid=#{jobid}"
                setSubmitStatus(ok, body)
            else
                IS_SUBMITTED = false
                msg = if content then content["content"]["msg"] else "Something went wrong :("
                setTextStatus(ok, msg)
    else
        setTextStatus(false, "You cannot resubmit the job")
        setLoadStatus(false)

################################################################
# Templates
################################################################
templateRow = (uid, name, content) ->
    delBtn = type: "div", cls: "btn btn-link btn-micro tooltipped tooltipped-e", onclick: (e) ->
        deleteTemplate(@uid)
        e.preventDefault()
        e.stopPropagation()
    delBtn = _mapper.parseMapForParent(delBtn)
    delBtn.innerHTML = "&times;"
    delBtn.uid = uid
    delBtn.setAttribute("aria-label", "Delete")
    title = type: "span", title: "#{name}"
    a = type: "a", href: "", cls: "menu-item", children: [delBtn, title], onclick: (e) ->
        # load template
        currentJob.settings = @content
        loadTemplate(currentJob)
        setTextStatus(true, "Template has been loaded")
        e.preventDefault()
        e.stopPropagation()
    a = _mapper.parseMapForParent(a)
    a.content = content
    return a

showTemplates = () ->
    _tempapi.show( ->
        elem = templateHeading.nextSibling
        while (elem)
            next = elem.nextSibling
            elem.parentNode.removeChild(elem)
            elem = next
    , (ok, json) ->
        parent = templateHeading.parentNode
        if ok
            arr = json["content"]["templates"]
            for item in arr
                uid = item["uid"]
                name = item["name"]
                content = item["content"]
                _mapper.parseMapForParent(templateRow(uid, name, content), parent)
        else
            setTextStatus(ok, "Something went wrong")
    )


deleteTemplate = (uid) ->
    _tempapi.delete(uid, null, (ok, json) ->
        msg = if ok then json["content"]["msg"] else "Something went wrong"
        setTextStatus(ok, msg)
        showTemplates()
    )

createTemplate = (name, content) ->
    setLoadStatus(true)
    data = name: "#{name}", content: content
    _tempapi.create(data, null, (ok, json) ->
        setLoadStatus(false)
        msg = if json then json["content"]["msg"] else "Something went wrong :("
        setTextStatus(ok, msg)
        # update templates if successful
        showTemplates() if ok
    )

# save template mechanism
new @FastEditor(templateButton, (status, value) ->
    createTemplate(value, currentJob.settings) if status
, "Save", "Cancel", "Name of template", false)

currentJob = DEFAULT_TEMPLATE
showTemplates()
loadTemplate(currentJob)

_util.addEventListener submitBtn, "click", (e) ->
    submitJob(currentJob)
    e.preventDefault()
    e.stopPropagation()
