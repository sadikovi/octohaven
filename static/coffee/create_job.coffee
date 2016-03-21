# `JobContainer` class that resembles Spark job to create, with all options
class JobContainer extends Reactable
  constructor: ->
    # State includes: name, (main) klass, driver memory, executor memory, delay, jar
    # Also features finder state (ls array, path array and current url accessed)
    @state =
      name: "#{Namer.generate()}"
      klass: "com.test.Main"
      dmemory: "4g"
      ememory: "4g"
      sparkOptions: ""
      jobOptions: ""
      delay: 0
      jar: null
      finder_url: "/api/v1/finder/home"
      finder_ls: []
      finder_path: []

  # Fetch finder data using url provided
  finder: (url) ->
    Api.doGet url, null, null, (ok, json) =>
      if ok
        @setState(finder_url: url, finder_ls: json.ls, finder_path: json.path)
      else
        # Here we just fail silently, UI will not be updated
        console.error "ERROR failed to parse finder object", ok, json

  componentWillMount: ->
    emitter.on OPTION_CHANGED, (id, value) =>
      @setState(name: "#{value}") if id == 1
      @setState(klass: "#{value}") if id == 2
      @setState(dmemory: "#{value}") if id == 3
      @setState(ememory: "#{value}") if id == 4
      @setState(sparkOptions: "#{value}") if id == 5
      @setState(jobOptions: "#{value}") if id == 6
      @setState(delay: value) if id == 100
    emitter.on FINDER_ELEM_CLICKED, (url) =>
      @finder(url)
    emitter.on FINDER_JAR_SELECTED, (realpath) =>
      @setState(jar: realpath)

  componentDidMount: ->
    @finder(@state.finder_url)

  componentWillUnmount: ->
    emitter.off OPTION_CHANGED
    emitter.off FINDER_ELEM_CLICKED
    emitter.off FINDER_JAR_SELECTED

  render: ->
    console.debug "Current state", @state
    @div({className: "segments"},
      Option.new(id: 1, key: "1", name: "Job name", desc: "Friendly job name"
        , default: "#{@state.name}"),
      Option.new(id: 2, key: "2", name: "Main class", desc: "Entrypoint for the Spark job"
        , default: "#{@state.klass}"),
      Option.new(id: 3, key: "3", name: "Driver memory", desc: "Memory for the driver program, e.g. 4g"
        , default: "#{@state.dmemory}"),
      Option.new(id: 4, key: "4", name: "Executor memory", desc: "Memory per Spark executor, e.g. 4g"
        , default: "#{@state.ememory}"),
      Option.new(id: 5, key: "5", name: "Spark options", desc: "Spark settings for the job, e.g. JVM, networking..."
        , default: "#{@state.sparkOptions}", textarea: true),
      Option.new(id: 6, key: "6", name: "Job options", desc: "Job options to pass to main class"
        , default: "#{@state.jobOptions}", textarea: true),
      FinderOption.new(ls: @state.finder_ls, path: @state.finder_path, jar: @state.jar),
      TimerOption.new(delay: @state.delay)
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
            @textarea({className: "input-monospace input-block", onChange: (event) => @handleInput(event)})
          else
            @input({type: "text", className: "input-monospace input-contrast input-block"
              , defaultValue: "#{@props.default}", onChange: (event) => @handleInput(event)})
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
    @div({className: "breadcrumb"}, elems)

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
    @div({className: "menu"}, elems)

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

ReactDOM.render JobContainer.new(), document.getElementById("content")
