# job settings elements
jobCanvas = document.getElementById("octohaven-job-settings")
unless jobCanvas
    throw new Error("Job settings canvas is undefined")
# file system elements
breadcrumbsElem = document.getElementById("octohaven-filelist-breadcrumbs")
filesElem = document.getElementById("octohaven-filelist-files")
selectedJarElem = document.getElementById("octohaven-selected-jar")
unless breadcrumbsElem and filesElem and selectedJarElem
    throw new Error("Cannot build file list")
# dependencies
filelist = new @Filelist
# job statuses
[JOB_CREATE, JOB_SUBMIT, JOB_SUCCESS, JOB_ERROR] = ["CREATE", "SUBMIT", "SUCCESS", "ERROR"]
statuses = [JOB_CREATE, JOB_SUBMIT, JOB_SUCCESS, JOB_ERROR]
# description of the current job (including settings, status, and jar file)
class CurrentJob
    constructor: (name, mainClass, driverMemory, executorMemory, options) ->
        # general job settings
        @settings = {}
        @settings["name"] = "#{name}"
        @settings["mainClass"] = "#{mainClass}"
        @settings["driverMemory"] = "#{driverMemory}"
        @settings["executorMemory"] = "#{executorMemory}"
        @settings["options"] = "#{options}"
        # jar settings
        @jar = elem: null, path: ""
        # current job status
        @status = JOB_CREATE

    setStatus: (status) ->
        throw new Error("Invalid status " + status) unless status in statuses
        @status = status

    setJar: (elem, path) ->
        @jar.elem = elem
        @jar.path = path

    isJarSet: -> @jar.elem?

    getJarElem: -> @jar.elem

    getJarPath: -> @jar.path

    setOption: (key, value) ->
        throw new Error("Option is not found") unless key of @settings
        @settings[key] = value

    getOption: (key) ->
        if key of @settings then @settings[key] else null

# initialise job
currentJob = new CurrentJob(@namer.generate(), "org.test.Main", "8g", "8g", "#")

################################################################
# Build job settings
################################################################

# returns entry for mapper for a job settings specified
jobSettingElem = (name, desc, value, canChange=true, onValueChanged) ->
    # header with setting name and tooltip attached
    span = @mapper.parseMapForParent(
        type: "span", cls: "text-mute tooltipped tooltipped-n", title: "#{name}")
    span.setAttribute("aria-label", "#{desc}")
    header = type: "div", cls: "one-fifth column", children: span
    # value body
    body = @mapper.parseMapForParent(type: "div", cls: "three-fifths column", title: "#{value}")
    body.setAttribute("data-attr", "fast-editor-texter")
    # change button, will trigger fast editor
    trigger = @mapper.parseMapForParent(type: "a", href: "#", title: "Change")
    trigger.setAttribute("data-attr", "fast-editor-trigger")
    changer = @mapper.parseMapForParent(
        if canChange then {type: "div", cls: "one-fifth column", children: trigger} else null)
    # overall block of settings
    block = @mapper.parseMapForParent(type: "div", cls: "segment", children:
        {type: "div", cls: "columns", children: [header, body, changer]})
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
    ]

@mapper.parseMapForParent(settings, jobCanvas)

################################################################
# Build file manager
################################################################

# fetching breadcrumbs
breadcrumbs = (dir) ->
    filelist.breadcrumbs(dir, ->
        breadcrumbsElem.innerHTML = ""
    , (json) =>
        return false unless json
        [arr, ls] = [[], json["content"]["breadcrumbs"]]
        for obj, i in ls
            if i < ls.length-1
                # not a last element
                elem =
                    type: "a"
                    cls: "section"
                    title: "#{obj["name"]}"
                    onclick: (e) ->
                        breadcrumbs(@path)
                        files(@path)
                elem = @mapper.parseMapForParent(elem)
                elem.path = obj["path"]
                arr.push(elem)
                arr.push(type: "div", cls: "separator", title: "/")
                elem = null
            else
                # last element
                arr.push(type: "div", cls: "active section", title: "#{obj["name"]}")
        @mapper.parseMapForParent(arr, breadcrumbsElem)
    )

selectJar = (elem, path) ->
    if currentJob.isJarSet()
        @util.removeClass(currentJob.getJarElem(), "selected")
        selectedJarElem.innerHTML = ""
    currentJob.setJar(elem, path)
    @util.addClass(elem, "selected")
    selectedJarElem.innerHTML = path

# fetching files
files = (dir) ->
    filelist.files(dir, ->
        filesElem.innerHTML = ""
    , (json) =>
        return false unless json
        [arr, ls] = [[], json["content"]["list"]]
        for obj in ls
            elem = null
            if obj["tp"] == "DIR"
                # it is a directory
                elem =
                    type: "a"
                    cls: "menu-item"
                    href: ""
                    title: "[dir] #{obj["name"]}"
                    onclick: (e) ->
                        breadcrumbs(@obj["path"])
                        files(@obj["path"])
                        e.preventDefault()
                        e.stopPropagation()
            else
                # it is a file
                elem =
                    type: "a"
                    cls: "menu-item"
                    href: ""
                    title: "[jar] #{obj["name"]}"
                    onclick: (e) ->
                        selectJar(@, @obj["path"])
                        e.preventDefault()
                        e.stopPropagation()
            elem = @mapper.parseMapForParent(elem)
            elem.obj = obj
            if currentJob.getJarPath() == elem.obj["path"]
                selectJar(elem, elem.obj["path"])
            arr.push(elem)
        @mapper.parseMapForParent(arr, filesElem)
    )

# initial call with an empty directory == ROOT
breadcrumbs("")
files("")
