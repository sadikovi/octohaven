_loader = @loader
_mapper = @mapper
_util = @util
_fasteditor = @fasteditor
_namer = @namer
FILE_API = @FILE_API
TEMPLATE_API = @TEMPLATE_API

# main content placeholder and status for requests
CONTENT = document.getElementById("content")
STATUS = document.getElementById("status")
throw new Error("Content is undefined") unless CONTENT and STATUS

hideStatus = -> _util.addClass STATUS, "hidden"

updateStatus = (ok, msg) ->
    _util.removeClass STATUS, "hidden"
    _util.removeClass STATUS, "error-box"
    _util.removeClass STATUS, "success-box"
    STATUS.innerHTML = "#{msg}"
    if ok
        _util.addClass STATUS, "success-box"
    else
        _util.addClass STATUS, "error-box"

# Current template to store data
template =
    jobname: "#{namer.generate()}"
    mainclass: ""
    drivermemory: "4g"
    executormemory: "4g"
    sparkoptions: ""
    joboptions: ""
    delay: "0"
    jar: null

# Options for template / job
initopt = (opt, onUpdate) ->
    throw new Error("Cannot resolve job option") if opt.getAttribute "default" == null
    fe = _fasteditor(opt, (ok, value) -> onUpdate?(value) if ok)
    opt.texter = fe.assets.texter
    opt

jobNameOption = initopt(document.getElementById("opt_job_name"), (value) ->
    template.jobname = "#{value}")
mainClassOption = initopt(document.getElementById("opt_main_class"), (value) ->
    template.mainclass = "#{value}")
driverMemoryOption = initopt(document.getElementById("opt_driver_memory"), (value) ->
    template.drivermemory = "#{value}")
executorMemoryOption = initopt(document.getElementById("opt_executor_memory"), (value) ->
    template.executormemory = "#{value}")
sparkOptionsOption = initopt(document.getElementById("opt_spark_options"), (value) ->
    template.sparkoptions = "#{value}")
jobOptionsOption = initopt(document.getElementById("opt_job_options"), (value) ->
    template.joboptions = "#{value}")

# Initialize timer
selecttimer = (delay) ->
    throw new Error("Cannot resolve delay option") unless delay.getAttribute "default"
    # remove selected from all delays and add selected to this delay, and update template
    for d in delays
        _util.removeClass d, "selected"
    _util.addClass delay, "selected"
    "#{delay.getAttribute "default"}"

inittimer = (delay) ->
    _util.addEventListener delay, "click", (e) ->
        template.delay = selecttimer(@)
        e.preventDefault()
        e.stopPropagation()
    delay

delay0sec = inittimer(document.getElementById("delay_0sec"))
delay10min = inittimer(document.getElementById("delay_10min"))
delay30min = inittimer(document.getElementById("delay_30min"))
delay1hrs = inittimer(document.getElementById("delay_1hrs"))
delay3hrs = inittimer(document.getElementById("delay_3hrs"))
delay24hrs = inittimer(document.getElementById("delay_24hrs"))
delays = [delay0sec, delay10min, delay30min, delay1hrs, delay3hrs, delay24hrs]

# Initialize finder
finder = document.getElementById("opt_finder")
breadcrumbs = document.getElementById("opt_finder_breadcrumbs")
ls = document.getElementById("opt_finder_ls")
selected = document.getElementById("opt_finder_selected")

throw new Error("Insufficient structure of finder") unless finder and breadcrumbs and ls and selected
finder.selected = null

updateSelected = (jarpath) -> selected.innerHTML = "Selected: #{jarpath}"

selectFile = (elem) ->
    if finder.selected
        _util.removeClass finder.selected, "selected"
    finder.selected = elem
    template.jar = elem.realpath
    updateSelected(template.jar)
    _util.addClass elem, "selected"

tree = (url) ->
    FILE_API.ls(before = ->
        breadcrumbs.innerHTML = ""
        ls.innerHTML = ""
        _util.addClass finder, "loading"
    , (ok, json) ->
        _util.removeClass finder, "loading"
        if ok
            path = json["payload"]["path"]
            content = json["payload"]["ls"]

            # construct breadcrumbs
            paths = []
            for p, i in path
                cls = "section"
                tpe = "a"
                if i == path.length - 1
                    cls = "#{cls} active"
                    tpe = "div"
                elem = mapper.parseMapForParent(type: tpe, cls: "#{cls}", title: "#{p["name"]}")
                elem.url = "#{p["url"]}"
                if i < path.length - 1
                    _util.addEventListener elem, "click", (e) ->
                        tree(@url) if @url; e.preventDefault(); e.stopPropagation()
                paths.push elem
                paths.push type: "div", cls: "separator", title: "/"
            mapper.parseMapForParent paths, breadcrumbs

            # construct tree
            files = []
            for f in content
                title = null
                if f["isdir"]
                    title = if f["name"] == "." or f["name"] == ".." then "#{f["name"]}" else
                        "[__] #{f["name"]}"
                else
                    title = "#{f["name"]}"
                elem = mapper.parseMapForParent(type: "a", cls: "menu-item", title: "#{title}")
                elem.href = "#"
                elem.url = "#{f["url"]}"
                elem.realpath = "#{f["realpath"]}"
                if f["isdir"]
                    _util.addEventListener elem, "click", (e) ->
                        tree(@url); e.preventDefault(); e.stopPropagation()
                else
                    _util.addEventListener elem, "click", (e) ->
                        selectFile(@); e.preventDefault(); e.stopPropagation()
                    if template.jar and elem.realpath == template.jar
                        selectFile(elem)
                files.push elem
            mapper.parseMapForParent files, ls
        else
            slate = mapper.parseMapForParent(
                type: "div"
                cls: "error-box"
                children: [
                    {type: "p", title: "#{if json then json["msg"] else "Really bad..."}"},
                    {type: "a", href: "#", title: "Reload", onclick: (e) ->
                        defaultTree(); e.preventDefault(); e.stopPropagation()}
                ], ls)
    , url)

defaultTree = -> tree("/api/v1/finder/home")

loadTemplate = (template) ->
    # load options
    jobNameOption.texter.innerHTML = "#{template.jobname}"
    mainClassOption.texter.innerHTML = "#{template.mainclass}"
    driverMemoryOption.texter.innerHTML = "#{template.drivermemory}"
    executorMemoryOption.texter.innerHTML = "#{template.executormemory}"
    sparkOptionsOption.texter.innerHTML = "#{template.sparkoptions}"
    jobOptionsOption.texter.innerHTML = "#{template.joboptions}"
    updateSelected(template.jar) if template.jar
    # Initialize tree
    defaultTree()
    # load delay
    if template.delay in (t.getAttribute("default") for t in delays)
        selecttimer(d) for d in delays when d.getAttribute("default") == template.delay
    else
        # if nothing was selected, choose minimum delay
        template.delay = selecttimer(delay_0sec)

loadTemplate(template)

# submit job button and create new template button
btnNewJob = document.getElementById("btn_job_new")
btnNewTemplate = document.getElementById("btn_template_new")

unless btnNewJob and btnNewTemplate
    throw new Error("Cannot locate action buttons")

# add editor on template, so you can type name for it
_fasteditor(btnNewTemplate, (ok, value) ->
    return false unless ok
    unless value
        updateStatus(false, "Template name is empty")
        return false
    # assign action on template button
    _util.addEventListener(btnNewTemplate, "click", (e) ->
        TEMPLATE_API.newTemplate(value, template
        , ->
            _util.addClass CONTENT, "loading"
            hideStatus()
        , (ok, json) ->
            _util.removeClass CONTENT, "loading"
            if ok
                updateStatus(ok,  json["payload"]["msg"])
            else
                updateStatus(ok,  if json then "Error: #{json["msg"]}" else "Unrecoverable error")
        )
    )
, oktext="Save", canceltext="Cancel", placeholder="", displayvalue=false)
