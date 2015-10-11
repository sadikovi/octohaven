jobCanvas = document.getElementById("octohaven-job-settings")
unless jobCanvas
    throw new Error("Job settings canvas is undefined")

################################################################
# Build job settings
################################################################

# returns entry for mapper for a job settings specified
jobSettingElem = (name, desc, value, canChange=true, onValueChanged) ->
    # header with setting name and tooltip attached
    span = type: "span",  cls: "text-mute tooltipped tooltipped-n", title: "#{name}"
    span = @mapper.parseMapForParent(span)
    span.setAttribute("aria-label", "#{desc}")
    header = type: "div", cls: "one-fifth column", children: span
    # value body
    body = type: "div", cls: "three-fifths column text-mono", title: "#{value}"
    body = @mapper.parseMapForParent(body)
    body.setAttribute("data-attr", "fast-editor-texter")
    # change button, will trigger fast editor
    trigger = @mapper.parseMapForParent(type: "a", href: "#", title: "Change")
    trigger.setAttribute("data-attr", "fast-editor-trigger")
    changer = if canChange then {type: "div", cls: "one-fifth column", children: trigger} else null
    changer = @mapper.parseMapForParent(changer)
    # overall block of settings
    block = {type: "div", cls: "segment", children: {type: "div", cls: "columns", children:
        [header, body, changer]}}
    block = @mapper.parseMapForParent(block)
    block.setAttribute("data-attr", "fast-editor")
    # create fast editor
    if canChange
        new @FastEditor(block, (status, value) -> onValueChanged?(status, value))
    # return map with all settings
    block

@jobSettings =
    name: @namer.generate()
    mainClass: "com.test.Main"
    driverMemory: "8g"
    executorMemory: "8g"
    options: "#"

map =
    type: "div"
    cls: "segments"
    children: [
        jobSettingElem("Job name", "Friendly job name", jobSettings.name, true, (ok, value) ->
            jobSettings.name = value if ok),
        jobSettingElem("Main class", "Main class as entrypoint for the job.", jobSettings.mainClass,
            true, (ok, value) -> jobSettings.mainClass = value if ok),
        jobSettingElem("Driver memory", "Memory for operations in a driver programme",
            jobSettings.driverMemory, true, (ok, value) -> jobSettings.driverMemory = value if ok),
        jobSettingElem("Executor memory", "Amount of memory for Spark executors",
            jobSettings.executorMemory, true, (ok, value) -> jobSettings.executorMemory = value if ok),
        jobSettingElem("Options", "Additional settings, e.g. JVM, networking, shuffle...",
            jobSettings.options, true, (ok, value) -> jobSettings.options = value if ok)
    ]

@mapper.parseMapForParent(map, jobCanvas)

################################################################
# Build file manager
################################################################
