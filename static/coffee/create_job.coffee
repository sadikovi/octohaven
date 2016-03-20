# `JobContainer` class that resembles Spark job to create, with all options
class JobContainer extends Reactable
  constructor: ->
    # State includes: name, (main) klass, driver memory, executor memory
    @state =
      name: "#{Namer.generate()}"
      klass: "com.test.Main"
      dmemory: "4g"
      ememory: "4g"
      delay: 0

  componentWillMount: ->
    emitter.on OPTION_CHANGED, (id, value) =>
      @setState(name: "#{value}") if id == 1
      @setState(klass: "#{value}") if id == 2
      @setState(dmemory: "#{value}") if id == 3
      @setState(ememory: "#{value}") if id == 4
      @setState(delay: value) if id == 100

  componentWillUnmount: ->
    emitter.off OPTION_CHANGED

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
      FinderOption.new(),
      TimerOption.new()
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
        @small({}, " (select jar file to use with main class provided)")
      )
    )

# Timer option as list of delay choices for the job
class TimerOption extends Reactable
  constructor: ->
    @state =
      selected: 0

  componentDidMount: ->
    @handleClick(@state.selected)

  handleClick: (seconds) ->
    @setState(selected: seconds)
    emitter.emit OPTION_CHANGED, 100, seconds
    console.debug "Emitted event", 100, seconds, Date.now()

  timer: (seconds, name) ->
    tag = if @state.selected == seconds then "selected" else ""
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
