# dependencies
_filelist = new @Filelist
_util = @util
_mapper = @mapper
_namer = @namer

# job settings elements
jobCanvas = document.getElementById("octohaven-job-settings")
throw new Error("Job settings canvas is undefined") unless jobCanvas
# file system elements
breadcrumbsElem = document.getElementById("octohaven-filelist-breadcrumbs")
filesElem = document.getElementById("octohaven-filelist-files")
selectedJarElem = document.getElementById("octohaven-selected-jar")
unless breadcrumbsElem and filesElem and selectedJarElem
    throw new Error("Cannot build file list")
# submit button and global status bar
submitBtn = document.getElementById("octohaven-submit-job")
statusBar = document.getElementById("octohaven-validation-status")
throw new Error("Submit requirements failed") unless submitBtn and statusBar
# job statuses
[JOB_CREATE, JOB_SUBMIT] = ["CREATE", "SUBMIT"]
statuses = [JOB_CREATE, JOB_SUBMIT]

# description of the current job (including settings, status, and jar file)
class CurrentJob
    constructor: (name, mainClass, driverMemory, executorMemory, options, jobconf) ->
        # general job settings
        @settings =
            name: "#{name}"
            mainClass: "#{mainClass}"
            driverMemory: "#{driverMemory}"
            executorMemory: "#{executorMemory}"
            options: "#{options}"
            jobconf: "#{jobconf}"
            delay: "#{delay}"
        # jar settings
        @jar = elem: null, path: ""
        # current job status
        @status = JOB_CREATE

    setStatus: (status) ->
        throw new Error("Invalid status " + status) unless status in statuses
        @status = status

    getStatus: -> @status

    setJar: (elem, path) ->
        @jar.elem = elem
        @jar.path = path

    isJarSet: -> @jar.elem?

    getJarElem: -> @jar.elem

    getJarPath: -> @jar.path

    setOption: (key, value) ->
        throw new Error("Option is not found") unless key of @settings
        @settings[key] = value

    getOption: (key) -> if key of @settings then @settings[key] else null

# initialise job
currentJob = new CurrentJob(_namer.generate(), "org.test.Main", "8g", "8g", "", "")

################################################################
# Build job settings
################################################################

# returns entry for mapper for a job settings specified
jobSettingElem = (name, desc, value, canChange=true, onValueChanged) ->
    # header with setting name and tooltip attached
    span = _mapper.parseMapForParent(
        type: "span", cls: "text-mute tooltipped tooltipped-n", title: "#{name}")
    span.setAttribute("aria-label", "#{desc}")
    header = type: "div", cls: "one-fifth column", children: span
    # value body
    body = _mapper.parseMapForParent(type: "div", cls: "three-fifths column", title: "#{value}")
    body.setAttribute("data-attr", "fast-editor-texter")
    # change button, will trigger fast editor
    trigger = _mapper.parseMapForParent(type: "a", href: "#", title: "Change")
    trigger.setAttribute("data-attr", "fast-editor-trigger")
    changer = _mapper.parseMapForParent(
        if canChange then {type: "div", cls: "one-fifth column", children: trigger} else null)
    # overall block of settings
    block = _mapper.parseMapForParent(type: "div", cls: "segment", children:
        {type: "div", cls: "columns", children: [header, changer, body]})
    block.setAttribute("data-attr", "fast-editor")
    # create fast editor
    if canChange
        new @FastEditor(block, (status, value) -> onValueChanged?(status, value))
    # return map with all settings
    block

settings =
    type: "div"
    cls: "segments"
    children: [
        # job name
        jobSettingElem("Job name", "Friendly job name", currentJob.getOption("name"), true,
            (ok, value) -> currentJob.setOption("name", value) if ok),
        # main class
        jobSettingElem("Main class", "Main class as entrypoint for the job.",
            currentJob.getOption("mainClass"), true,
            (ok, value) -> currentJob.setOption("mainClass", value) if ok),
        # driver memory
        jobSettingElem("Driver memory", "Memory for operations in a driver programme",
            currentJob.getOption("driverMemory"), true,
            (ok, value) -> currentJob.setOption("driverMemory", value) if ok),
        # executor memory
        jobSettingElem("Executor memory", "Amount of memory for Spark executors",
            currentJob.getOption("executorMemory"), true,
            (ok, value) -> currentJob.setOption("executorMemory", value) if ok),
        # additional job options
        jobSettingElem("Options", "Additional settings, e.g. JVM, networking, shuffle...",
            currentJob.getOption("options"), true,
            (ok, value) -> currentJob.setOption("options", value) if ok)
        jobSettingElem("Job options", "Specific job [not Spark] options to pass to entrypoint",
            currentJob.getOption("jobconf"), true,
            (ok, value) -> currentJob.setOption("jobconf", value) if ok)
    ]

_mapper.parseMapForParent(settings, jobCanvas)

################################################################
# Build file manager
################################################################

# fetching breadcrumbs
breadcrumbs = (dir) ->
    _filelist.breadcrumbs(dir, ->
        breadcrumbsElem.innerHTML = ""
    , (ok, json) =>
        if ok
            [arr, ls] = [[], json["content"]["breadcrumbs"]]
            for obj, i in ls
                if i < ls.length-1
                    elem =
                        type: "a"
                        cls: "section"
                        title: "#{obj["name"]}"
                        onclick: (e) ->
                            breadcrumbs(@path)
                            files(@path)
                    elem = _mapper.parseMapForParent(elem)
                    elem.path = obj["path"]
                    arr.push(elem)
                    arr.push(type: "div", cls: "separator", title: "/")
                else
                    # last element
                    arr.push(type: "div", cls: "active section", title: "#{obj["name"]}")
            _mapper.parseMapForParent(arr, breadcrumbsElem)
        else if json
            setTextStatus(json["content"]["msg"], false)
        else
            setTextStatus("Something went wrong :(", false)
    )

selectJar = (elem, path) ->
    if currentJob.isJarSet()
        _util.removeClass(currentJob.getJarElem(), "selected")
        selectedJarElem.innerHTML = ""
    currentJob.setJar(elem, path)
    _util.addClass(elem, "selected")
    selectedJarElem.innerHTML = path

# fetching files
files = (dir) ->
    _filelist.files(dir, ->
        filesElem.innerHTML = ""
    , (ok, json) =>
        if ok
            [arr, ls] = [[], json["content"]["list"]]
            for obj in ls
                elem = type: "a", cls: "menu-item", href: ""
                if obj["tp"] == "DIR"
                    # it is a directory
                    elem["title"] = "[dir] #{obj["name"]}"
                    elem["onclick"] = (e) ->
                        breadcrumbs(@obj["path"])
                        files(@obj["path"])
                        e.preventDefault()
                        e.stopPropagation()
                else
                    # it is a file
                    elem["title"] = "[jar] #{obj["name"]}"
                    elem["onclick"] = (e) ->
                        selectJar(@, @obj["path"])
                        e.preventDefault()
                        e.stopPropagation()
                elem = _mapper.parseMapForParent(elem)
                elem.obj = obj
                if currentJob.getJarPath() == elem.obj["path"]
                    selectJar(elem, elem.obj["path"])
                arr.push(elem)
            _mapper.parseMapForParent(arr, filesElem)
        else if json
            setTextStatus(json["content"]["msg"], false)
        else
            setTextStatus("Something went wrong :(", false)
    )

# initial call with an empty directory == ROOT
breadcrumbs("")
files("")

################################################################
# Delay job
################################################################
delayNow = document.getElementById("octohaven-job-delay-now")
delayNow.diff = 0
delay10min = document.getElementById("octohaven-job-delay-10min")
delay10min.diff = 10*60
delay30min = document.getElementById("octohaven-job-delay-30min")
delay30min.diff = 30*60
delay1hr = document.getElementById("octohaven-job-delay-1hr")
delay1hr.diff = 1*60*60
delay3hrs = document.getElementById("octohaven-job-delay-3hrs")
delay3hrs.diff = 3*60*60

delays = [delayNow, delay10min, delay30min, delay1hr, delay3hrs]

changeDelay = (delay) ->
    currentJob.setOption("delay", delay.diff)
    _util.removeClass(each, "selected") for each in delays
    _util.addClass(delay, "selected")

for delay in delays
    _util.addEventListener delay, "click", (e) ->
        changeDelay(@)
        e.preventDefault()
        e.stopPropagation()
changeDelay(delayNow)

################################################################
# Submit job
################################################################

setLoadStatus = (load) ->
    if load then _util.addClass(statusBar, "loading") else _util.removeClass(statusBar, "loading")

setSubmitStatus = (ok, internal) ->
    statusBar.innerHTML = ""
    mode = if ok then "success-box" else "error-box"
    obj = type: "div", cls: mode, children: internal
    _mapper.parseMapForParent(obj, statusBar)

setTextStatus = (ok, text) ->
    setSubmitStatus(ok, type: "span", title: "#{text}")

submitJob = (job) ->
    setLoadStatus(true)
    if job.getStatus() == JOB_CREATE
        job.setStatus(JOB_SUBMIT)
        # extracting latest changes from the current job
        settings = job.settings
        settings["jar"] = job.jar.path
        resolver = new JobResolver
        resolver.submit JSON.stringify(settings), null, (ok, content) ->
            setLoadStatus(false)
            if ok
                # extract job id
                msg = content["content"]["msg"]
                jobid = content["content"]["jobid"]
                body = type: "span", title: "#{msg}. ", children:
                    type: "a", title: "View details", href: "/job?=#{jobid}"
                setSubmitStatus(ok, body)
            else
                job.setStatus(JOB_CREATE)
                msg = if content then content["content"]["msg"] else "Something went wrong :("
                setTextStatus(ok, msg)
    else
        setTextStatus(false, "You cannot resubmit the job")
        setLoadStatus(false)

# attach click event on button, so we can submit
_util.addEventListener submitBtn, "click", (e) ->
    submitJob(currentJob)
    e.preventDefault()
    e.stopPropagation()
