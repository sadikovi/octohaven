serverStatus = document.getElementById("octohaven-spark-server-status")
unless serverStatus
    throw new Error("Server entries are unrecognized")
jobCanvas = document.getElementById("octohaven-job-settings")
unless jobCanvas
    throw new Error("Job settings canvas is undefined")

################################################################
# Request Spark Cluster status and set all the elements.
################################################################

# setting status of Spark cluster on web UI
setStatus = (status) ->
    # clean up status
    serverStatus.className = ""
    if status == false
        serverStatus.innerHTML = "#{@Status.STATUS_PENDING}"
        @util.addClass(serverStatus, "text-mute")
    else if status == 0
        @util.addClass(serverStatus, "text-green")
        serverStatus.innerHTML = "#{@Status.STATUS_READY}"
    else if status == -1
        @util.addClass(serverStatus, "text-yellow")
        serverStatus.innerHTML = "#{@Status.STATUS_BUSY}"
    else
        @util.addClass(serverStatus, "text-red")
        serverStatus.innerHTML = "#{@Status.STATUS_UNREACHABLE}"

reloadStatus = ->
    status = new @Status
    # run this function before performing any requests
    before = ->
        setStatus(false)
    # once we have received response set all the elements to reflect change
    after = (status, uiAddress, masterAddress) ->
        setStatus(status)
    # ask status for Spark Cluster info
    status.requestStatus(before, after)

# reload status
reloadStatus?()

################################################################
# Build job settings
################################################################

# returns entry for mapper for a job settings specified
jobSetting = (name, desc, value, canChange=true, onValueChanged) ->
    # header with setting name and tooltip attached
    span = {type: "span",  cls: "text-mute tooltipped tooltipped-n", title: "#{name}"}
    span = @mapper.parseMapForParent(span)
    span.setAttribute("aria-label", "#{desc}")
    header = {type: "div", cls: "one-fifth column", children: span}
    # value body
    body = {type: "div", cls: "three-fifths column text-mono", title: "#{value}"}
    body = @mapper.parseMapForParent(body)
    body.setAttribute("data-attr", "fast-editor-texter")
    # change button, will trigger fast editor
    trigger = @mapper.parseMapForParent({type: "a", href: "#", title: "Change"})
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

map =
    type: "div"
    cls: "segments"
    children: [
        jobSetting("Job name", "Friendly job name", @namer.generate(), true),
        jobSetting("Spark URL", "Spark Master URL", "spark://test-url:7077", false)
        jobSetting("Main class", "Main class as entrypoint for the job.", "com.test.Main", true),
        jobSetting("Driver memory", "Memory for operations in a driver programme", "8g", true),
        jobSetting("Executor memory", "Amount of memory for Spark executors", "8g", true),
        jobSetting("Options", "Additional settings, e.g. JVM, networking, shuffle...", "#", true)
    ]

@mapper.parseMapForParent(map, jobCanvas)
