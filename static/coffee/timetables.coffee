# Building filters
class TimetableFilterController extends Reactable
  constructor: ->
    @state =
      enabled: ALL

  refreshForStatus: (status) ->
    @setState(enabled: status)
    dispatcher.dispatch type: TIMETABLE_FILTER_SELECTED, data: status
    console.debug "Dispatched event: #{TIMETABLE_FILTER_SELECTED}", status, Date.now()

  componentWillMount: ->
    emitter.on TIMETABLE_FILTER_SELECTED, (filter) =>
      @refreshForStatus(filter)
    emitter.on TIMETABLE_ACTION_FIRED, =>
      @refreshForStatus(@state.enabled)
    # Fire initial refresh before component is mounted to render once only
    @refreshForStatus @state.enabled

  componentWillUnmount: ->
    emitter.off TIMETABLE_FILTER_SELECTED
    emitter.off TIMETABLE_ACTION_FIRED

  render: ->
    TimetableFilterView.new(enabled: @state.enabled)

class TimetableFilterView extends Reactable
  render: ->
    @nav({className: "menu"},
      @div({className: "menu-heading"}, "Filters"),
      (TimetableFilter.new(key: name, name: name, enabled: name == @props.enabled) for name in TIMETABLE_STATUSES)
    )

class TimetableFilter extends Reactable
  handleClick: (event) ->
    emitter.emit TIMETABLE_FILTER_SELECTED, @props.name
    console.debug "Emitted event", TIMETABLE_FILTER_SELECTED, @props.name
    event.preventDefault()
    event.stopPropagation()

  render: ->
    selected = if @props.enabled then "selected" else ""
    @a({className: "#{selected} menu-item", href: "#", onClick: (event) => @handleClick(event)},
      "#{@props.name}")

# Timetable controller and view
class TimetableController extends Reactable
  constructor: ->
    @state =
      data: []
      okay: true

  componentWillMount: ->
    emitter.on TIMETABLE_DATA_REQUESTED, =>
      @setState(data: [], okay: true)
    emitter.on TIMETABLE_DATA_ARRIVED, (ok, data) =>
      @setState(data: data, okay: ok)

  componentWillUnmount: ->
    emitter.off TIMETABLE_DATA_REQUESTED
    emitter.on TIMETABLE_DATA_ARRIVED

  render: ->
    if @state.okay
      TimetableView.new(data: @state.data)
    else
      @div({className: "blankslate"},
        @h1({className: "text-thin"}, "Could not load timetables"),
        @p({}, "Open dev console to investigate further")
      )

class TimetableView extends Reactable
  render: ->
    @div({className: "segments"},
      (TimetableRecord.new(key: row.uid, name: row.name, status: row.status, url: row.url
        , resume_url: row.resume_url, pause_url: row.pause_url, stats: row.stats) for row in @props.data)
    )

class TimetableRecord extends Reactable
  constructor: ->
    @state =
      enabled: true
      btnName: null

  handleClick: (url) ->
    @setState(enabled: false, btnName: "...")
    Api.doGet url, null, null, null, (ok, json) =>
      @setState(btnName: "Error") unless ok
      emitter.emit TIMETABLE_ACTION_FIRED, url
      console.debug "Emitted event", TIMETABLE_ACTION_FIRED, url

  resolveNameAndUrl: (resume, pause) ->
    if resume
      ["Resume", resume]
    else if pause
      ["Pause", pause]
    else
      [null, null]

  render: ->
    # Name of action button and corresponding URL
    [btnName, url] = @resolveNameAndUrl(@props.resume_url, @props.pause_url)
    if @state.btnName
      btnName = "#{@state.btnName}"
    # Whether or not active button is enabled
    isEnabled = @state.enabled

    @div({className: "segment"},
      @div({className: "columns"},
        @div({className: "one-sixth column"},
          @span({className: "#{timetableStatusLabel(@props.status)}"}, "#{@props.status}"),
        )
        @div({className: "one-third column"},
          @a({className: "css-truncate css-truncate-target", href: "#{@props.url}"}, "#{@props.name}"),
        ),
        @div({className: "one-third column"},
          @div({}, "Jobs so far: #{@props.stats.jobs}"),
          @div({}, "Last run: ",
            if @props.stats.lasttime and @props.stats.last_url
              @a({href: "#{@props.stats.last_url}"}, "#{Util.timestampToDate(@props.stats.lasttime)}")
            else
              @span({}, "hasn't happened yet")
          )
        ),
        @div({className: "one-sixth column"},
          if btnName and url then @div({className: "btn btn-compact #{if isEnabled then "" else "btn-disabled"}"
            , onClick: => @handleClick(url)}, "#{btnName}") else @span()
        )
      )
    )

# Store
class ModelStore
  @xhr = null
  # Dispatch token for current callback
  @dispatchToken = dispatcher.register (payload) =>
    if payload.type == TIMETABLE_FILTER_SELECTED
      console.log "Checking xhr...", @xhr
      @xhr?.abort()
      status = payload.data
      url = "/api/v1/timetable/list"
      @xhr = Api.doGet(url, null, {status: status}, ->
        emitter.emit TIMETABLE_DATA_REQUESTED
        console.debug "Emitted event", TIMETABLE_DATA_REQUESTED, Date.now()
      , (okay, json) =>
        console.error "ERROR", json unless okay
        emitter.emit TIMETABLE_DATA_ARRIVED, okay, json?.rows
        console.debug "Emitted event", TIMETABLE_DATA_ARRIVED, okay, Date.now()
      )
    else
      console.warn "Unrecognized dispatch object", payload

ReactDOM.render TimetableController.new(), document.getElementById("content")
ReactDOM.render TimetableFilterController.new(), document.getElementById("filters")
