# `JobContainer` class that resembles Spark job to create, with all options
class JobContainer extends Reactable
  constructor: ->
    # State includes: name, (main class) entrypoint, driver memory, executor memory, delay, jar
    # Also features finder state (ls array, path array and current url accessed)
    @state =
      name: "#{Namer.generate()}"
      entrypoint: "com.test.Main"
      dmemory: "4g"
      ememory: "4g"
      options: ""
      jobconf: ""
      delay: 0
      jar: null
      finder_url: "/api/v1/finder/home"
      finder_ls: []
      finder_path: []
      note_state: "hidden"
      note_message: ""
      submit_url: "/api/v1/job/create"
      submit_enable: true
      save_template_url: "/api/v1/template/create"

  # Select parameters and return payload
  getPayload: ->
    payload =
      name: @state.name
      entrypoint: @state.entrypoint
      dmemory: @state.dmemory
      ememory: @state.ememory
      options: @state.options
      jobconf: @state.jobconf
      delay: @state.delay
      jar: @state.jar
    payload

  # Fetch finder data using url provided
  finder: (url) ->
    Api.doGet url, null, null, null, (ok, json) =>
      if ok
        @setState(finder_url: url, finder_ls: json.ls, finder_path: json.path)
      else
        # Here we just fail silently, UI will not be updated
        console.error "ERROR failed to parse finder object", ok, json

  submit: ->
    Api.doPost @state.submit_url, {"Content-Type": "application/json"}, @getPayload(), =>
      @setState(note_state: "loading", note_message: "", submit_enable: false)
      console.debug "Submitting the job for state", @state
    , (ok, json) =>
      if ok
        txt = "Job created successfully. To resubmit the job, please refresh the web-page"
        @setState(note_state: "success", note_message: "#{txt}", submit_enable: false)
        console.debug "Created new job", ok, json
      else
        txt = "Failed to create job, reason: #{if json?.msg then json.msg else "unknown"}"
        @setState(note_state: "error", note_message: "#{txt}", submit_enable: true)
        console.error "Failed to create job", ok, json

  saveTemplate: ->
    Api.doPost @state.save_template_url, {"Content-Type": "application/json"}, @getPayload(), =>
      @setState(note_state: "loading", note_message: "")
      console.debug "Saving template", @state
    , (ok, json) =>
      if ok
        txt = "Template '#{json.name}' created successfully"
        @setState(note_state: "success", note_message: "#{txt}")
        console.info "Created new template", ok, json
        emitter.emit TEMPLATE_SAVED
        console.debug "Emitted event", TEMPLATE_SAVED, Date.now()
      else
        txt = "Failed to create template, reason: #{json?.msg ? "unknown"}"
        @setState(note_state: "error", note_message: "#{txt}")
        console.error "Failed to create template", ok, json

  componentWillMount: ->
    emitter.on OPTION_CHANGED, (id, value) =>
      @setState(name: "#{value}") if id == 1
      @setState(entrypoint: "#{value}") if id == 2
      @setState(dmemory: "#{value}") if id == 3
      @setState(ememory: "#{value}") if id == 4
      @setState(options: "#{value}") if id == 5
      @setState(jobconf: "#{value}") if id == 6
      @setState(delay: value) if id == 100
    emitter.on FINDER_ELEM_CLICKED, (url) =>
      @finder(url)
    emitter.on FINDER_JAR_SELECTED, (realpath) =>
      @setState(jar: realpath)
    emitter.on JOB_SUBMIT_REQUESTED, =>
      @submit()
    emitter.on TEMPLATE_LOADING, (content) =>
      console.log "Reloading job..."
      @setState(content)
    emitter.on TEMPLATE_SAVING, =>
      @saveTemplate()

  componentDidMount: ->
    @finder(@state.finder_url)

  componentWillUnmount: ->
    emitter.off OPTION_CHANGED
    emitter.off FINDER_ELEM_CLICKED
    emitter.off FINDER_JAR_SELECTED
    emitter.off JOB_SUBMIT_REQUESTED
    emitter.off TEMPLATE_LOADING
    emitter.off TEMPLATE_SAVING

  render: ->
    console.debug "Current state", @state
    @div({className: "segments"},
      Option.new(id: 1, key: "1", name: "Job name", desc: "Friendly job name"
        , default: "#{@state.name}"),
      Option.new(id: 2, key: "2", name: "Main class", desc: "Entrypoint for the Spark job"
        , default: "#{@state.entrypoint}"),
      Option.new(id: 3, key: "3", name: "Driver memory", desc: "Memory for the driver program, e.g. 4g"
        , default: "#{@state.dmemory}"),
      Option.new(id: 4, key: "4", name: "Executor memory", desc: "Memory per Spark executor, e.g. 4g"
        , default: "#{@state.ememory}"),
      Option.new(id: 5, key: "5", name: "Spark options", desc: "Spark settings for the job, e.g. JVM, networking..."
        , default: "#{@state.options}", textarea: true),
      Option.new(id: 6, key: "6", name: "Job options", desc: "Job options to pass to main class"
        , default: "#{@state.jobconf}", textarea: true),
      FinderOption.new(ls: @state.finder_ls, path: @state.finder_path, jar: @state.jar),
      TimerOption.new(delay: @state.delay),
      MessageBoard.new(message: @state.note_message, state: @state.note_state),
      ControlPanel.new(submit: @state.submit_enable)
    )

# Each option requires id (for events), name, description. Default value is optional, and is empty
# if nothing else is provided.
class Option extends Reactable
  handleInput: (event) ->
    emitter.emit OPTION_CHANGED, @props.id, event.target.value
    console.debug "Emitted event", @props.id, event.target.value, Date.now()

  render: ->
    @div({className: "segment"},
      @div({className: "columns"},
        @div(className: "one-fourth column",
          @span({className: "tooltipped tooltipped-n text-bold", "aria-label": "#{@props.desc}"},
            "#{@props.name}")
        ),
        @div({className: "three-fourths column"},
          if @props.textarea
            @textarea({className: "input-monospace input-block", value: "#{@props.default}"
              , onChange: (event) => @handleInput(event)})
          else
            @input({type: "text", className: "input-monospace input-block"
              , value: @props.default, onChange: (event) => @handleInput(event)})
        )
      )
    )

# Finder option to select jar file
class FinderOption extends Reactable
  render: ->
    @div({className: "segment"},
      @h2({className: "text-thin"},
        "Finder",
        @small({}, " (jar file to use with provided main class)")
      ),
      FinderPath.new(path: @props.path),
      FinderLs.new(ls: @props.ls, jar: @props.jar)
    )

# Sub-option of the finder, represents breadcrumbs of path being currently accessed
class FinderPath extends Reactable
  render: ->
    elems = []
    n = @props.path.length
    for elem, i in @props.path
      if i < (n - 1)
        elems.push FinderPathElem.new(key: "#{elem.realpath}", active: true, elem: elem)
        elems.push @div({key: "#{elem.realpath}-separator", className: "separator"}, "/")
      else
        elems.push FinderPathElem.new(key: "#{elem.realpath}", active: false, elem: elem)
    @div({className: "breadcrumb"},
      @div({className: "text-mono separator"}, "$ ls "),
      elems
    )

# Element of finder path sub-option
class FinderPathElem extends Reactable
  handleClick: (event, url) ->
    event.preventDefault()
    emitter.emit FINDER_ELEM_CLICKED, url
    console.debug "Emitted event", FINDER_ELEM_CLICKED, url, Date.now()

  render: ->
    if @props.active
      @a({className: "section", href: "#", onClick: (event) => @handleClick(event, @props.elem.url)}
        , "#{@props.elem.name}")
    else
      @div({className: "active section"}, "#{@props.elem.name}")

# Sub-option of finder, represents list of files/folders for the path accessed
class FinderLs extends Reactable
  select: (elem) ->
    !elem.isdir and elem.realpath == @props.jar

  render: ->
    elems = (FinderLsElem.new(key: "#{elem.realpath}", elem: elem, selected: @select(elem)) for elem in @props.ls)
    @div({},
      @div({className: "menu"}, elems),
      @div({className: "text-blur #{if !@props.jar then "hidden" else ""}"}, "> #{@props.jar}")
    )


# Element of finder ls sub-option
class FinderLsElem extends Reactable
  handleClick: (event, elem) ->
    event.preventDefault()
    if elem.isdir
      emitter.emit FINDER_ELEM_CLICKED, elem.url
      console.debug "Emitted event", FINDER_ELEM_CLICKED, elem.url, Date.now()
    else
      emitter.emit FINDER_JAR_SELECTED, elem.realpath
      console.debug "Emitted event", FINDER_JAR_SELECTED, elem.realpath, Date.now()

  render: ->
    tn = @props.elem.name
    elemName = if @props.elem.isdir and tn != ".." and tn != "." then "#{tn}/" else "#{tn}"
    @a({className: "menu-item #{if @props.selected then "selected" else ""}", href: "#"
      , onClick: (event) => @handleClick(event, @props.elem)}, elemName)

# Timer option as list of delay choices for the job
class TimerOption extends Reactable
  handleClick: (seconds) ->
    emitter.emit OPTION_CHANGED, 100, seconds
    console.debug "Emitted event", 100, seconds, Date.now()

  timer: (seconds, name) ->
    tag = if @props.delay == seconds then "selected" else ""
    @li({id: seconds, className: "filter-item #{tag}", onClick: => @handleClick(seconds)}, "#{name}")

  render: ->
    @div({className: "segment"},
      @h2({className: "text-thin"},
        "Timer",
        @small({}, " (when to run the job)")
      ),
      @ul({className: "small filter-list"},
        @timer(0, "Right away"),
        @timer(600, "In 10 minutes"),
        @timer(1800, "In 30 minutes"),
        @timer(3600, "In 1 hour"),
        @timer(10800, "In 3 hours"),
        @timer(86400, "Next day")
      )
    )

# Notification board, displays success messages or errors during requests
class MessageBoard extends Reactable
  HIDDEN = "hidden"
  LOADING = "loading"
  ERROR = "error"
  SUCCESS = "success"

  render: ->
    [segmentClass, boxClass] = ["", ""]

    if @props.state == HIDDEN
      segmentClass = "hidden"
      boxClass = ""
    else if @props.state == LOADING
      segmentClass = "loading"
      boxClass = "hidden"
    else if @props.state == ERROR
      segmentClass = ""
      boxClass = "error-box"
    else if @props.state = SUCCESS
      segmentClass = ""
      boxClass = "success-box"

    @div({className: "#{segmentClass} segment"},
      @div({className: "#{boxClass}"},
        @p({}, @props.message)
      )
    )

# Controls to submit a job and save as template
class ControlPanel extends Reactable
  submitClick: () ->
    emitter.emit JOB_SUBMIT_REQUESTED
    console.debug "Emitted event", JOB_SUBMIT_REQUESTED, Date.now()

  saveTemplateClick: () ->
    emitter.emit TEMPLATE_SAVING
    console.debug "Emitted event", TEMPLATE_SAVING, Date.now()

  render: ->
    @div({className: "segment"},
      @div({className: "breadcrumb"},
        @div({className: "section"},
          @div({className: "btn btn-success #{if @props.submit then "" else "btn-disabled"}"
            , onClick: => @submitClick()}, "Submit")
        ),
        @div({className: "separator"}, " | "),
        @div({className: "section"},
          @div({className: "btn btn-primary", onClick: => @saveTemplateClick()}, "Save as template")
        )
      )
    )

# Class to handle template rendering
class TemplatesContainer extends Reactable
  constructor: ->
    @state =
      loading: false
      data: []
      url: "/api/v1/template/list"

  reloadTemplates: (url) ->
    Api.doGet url, null, null, =>
      @setState(loading: true, data: [])
    , (ok, json) =>
      if ok
        console.info "Successfully loaded templates", ok, json
        @setState(loading: false, data: json?.data)
      else
        console.error "Failed to load templates", ok, json
        @setState(loading: false, data: [])

  componentWillMount: ->
    emitter.on TEMPLATE_DELETED, (url) =>
      @reloadTemplates(url)
    emitter.on TEMPLATE_SAVED, =>
      @reloadTemplates(@state.url)

  componentDidMount: ->
    @reloadTemplates(@state.url)

  componentWillUnmount: ->
    emitter.off TEMPLATE_DELETED
    emitter.off TEMPLATE_SAVED

  render: ->
    Templates.new(templates: @state.data)

class Templates extends Reactable
  render: ->
    @nav({className: "menu"},
      @div({className: "menu-heading"}, "Templates"),
      (Template.new(key: x.uid, name: x.name, url: x.delete_and_list_url, content: x.content) for x in @props.templates)
    )

class Template extends Reactable
  deleteAndRefresh: (event, url) ->
    emitter.emit TEMPLATE_DELETED, url
    console.debug "Emitted event", TEMPLATE_DELETED, Date.now()
    event.preventDefault()
    event.stopPropagation()

  load: (event, content) ->
    emitter.emit TEMPLATE_LOADING, content
    console.debug "Emitted event", TEMPLATE_LOADING, content, Date.now()
    event.preventDefault()
    event.stopPropagation()

  render: ->
    @div({className: "menu-item"},
      @p({},
        @a({href: "#", onClick: (event) => @load(event, @props.content)}, "#{@props.name}")
      ),
      @a({className: "link-muted", href: "#"
        , onClick: (event) => @deleteAndRefresh(event, @props.url)}, "Delete")
    )

ReactDOM.render JobContainer.new(), document.getElementById("content")
ReactDOM.render TemplatesContainer.new(), document.getElementById("templates")
