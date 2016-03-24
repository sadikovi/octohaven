# Building filters
class Filter extends Reactable
  handleClick: (event, status) ->
    emitter.emit JOB_FILTER_SELECTED, status
    console.debug "Emitted event", JOB_FILTER_SELECTED, status, Date.now()
    event.preventDefault()
    event.stopPropagation()

  render: ->
    tag = if @props.selected then "selected" else ""
    @a({href: "/api", className: "menu-item #{tag}"
      , onClick: (event) => @handleClick(event, @props.status)}, "#{@props.status}")

class FilterList extends Reactable
  constructor: ->
    @state =
      selected: ALL

  refreshForStatus: (status) ->
    @setState(selected: status)
    dispatcher.dispatch type: JOB_FILTER_SELECTED, data: status
    console.debug "Dispatched event: #{JOB_FILTER_SELECTED}", status, Date.now()

  componentWillMount: ->
    emitter.on JOB_CLOSED_ARRIVED, (url, okay) =>
      console.debug "Attempt to close the job", url, okay, Date.now()
      console.debug "Refresh UI, since job was closed"
      @refreshForStatus @state.selected
    emitter.on JOB_FILTER_SELECTED, (status) =>
      @refreshForStatus status
    # Fire initial refresh before component is mounted to render once only
    @refreshForStatus @state.selected

  componentWillUnmount: ->
    emitter.off JOB_CLOSED_ARRIVED

  filter: (status) ->
    Filter.new(key: "#{status}", status: status, selected: status == @state.selected)

  render: ->
    @nav({className: "menu"},
      @div({className: "menu-heading"}, "Filters"),
      (@filter(status) for status in STATUS_LIST)
    )

# Building job list
class JobBox extends Reactable
  constructor: ->
    @state =
      data: []
      okay: true
      pending: false

  componentWillMount: ->
    emitter.on JOB_DATA_REQUESTED, (status) =>
      @setState(pending: true)
    emitter.on JOB_DATA_ARRIVED, (okay, rows) =>
      @setState(okay: okay, data: rows, pending: false)

  componentWillUnmount: ->
    emitter.off JOB_DATA_REQUESTED
    emitter.off JOB_DATA_ARRIVED

  render: ->
    if @state.pending
      @div({className: "loading segment"})
    else
      if @state.okay
        @div({}, Table.new(rows: @state.data))
      else
        @div({className: "blankslate"},
          @h1({className: "text-thin"}, "Could not load jobs"),
          @p({}, "Open dev console to investigate further")
        )

class Table extends Reactable
  render: ->
    @div({className: "segments"}, (Row.new(r: row, key: row.uid) for row in @props.rows))

class Row extends Reactable
  render: ->
    @div({className: "segment"},
      @div({className: "columns"},
        Status.new(className: "one-sixth column", label: "#{@props.r.status}", close: @props.r.close),
        Link.new(className: "one-third column", url: "#{@props.r.url}", label: "#{@props.r.name}"),
        Created.new(className: "one-third column", label: "#{diff(@props.r.createtime)}"),
        Action.new(className: "one-sixth column", action: @props.r.close)
      )
    )

class Status extends Reactable
  render: ->
    @div({className: "#{@props.className}"},
      @span({className: "#{statusLabel(@props.label)}"}, "#{@props.label}")
    )

class Link extends Reactable
  render: ->
    @div({className: "#{@props.className}"},
      @a({className: "css-truncate css-truncate-target", href: "#{@props.url}"}, "#{@props.label}")
    )

class Created extends Reactable
  render: ->
    @div({className: "#{@props.className}"},
      @span({className: "text-mute"}, "Created "),
      @span({}, "#{@props.label}")
    )

class Action extends Reactable
  constructor: ->
    @state =
      clicked: false
      txt: "Close"

  handleClick: ->
    @setState(clicked: true)
    dispatcher.dispatch type: JOB_CLOSED, data: @props.action

  render: ->
    @div({className: "#{@props.className}"},
      if @props.action
        isOff = if @state.clicked then "btn-disabled" else ""
        @div({className: "btn btn-compact #{isOff}", onClick: => @handleClick()}, "Close")
      else
        null
    )

# Store
class ModelStore
  # Current request in progress, null, if there is nothing pending
  @xhr = null
  # Dispatch token for current callback
  @dispatchToken = dispatcher.register (payload) =>
    if payload.type == JOB_FILTER_SELECTED
      console.log "Checking xhr...", @xhr
      @xhr?.abort()
      status = payload.data
      url = "/api/v1/job/list"
      @xhr = Api.doGet(url, null, {status: status}, ->
        emitter.emit JOB_DATA_REQUESTED, status
        console.debug "Emitted event", JOB_DATA_REQUESTED, status, Date.now()
      , (okay, data) =>
        console.error "ERROR", data unless okay
        emitter.emit JOB_DATA_ARRIVED, okay, data?.rows
        console.debug "Emitted event", JOB_DATA_ARRIVED, okay, Date.now()
      )
    else if payload.type == JOB_CLOSED
      url = payload.data
      Api.doGet(url, null, null, null, (okay, data) =>
        console.error "ERROR", data unless okay
        emitter.emit JOB_CLOSED_ARRIVED, url, okay
        console.debug "Emitted event", JOB_CLOSED_ARRIVED, url, okay, Date.now()
      )
    else
      console.warn "Unrecognized dispatch object", payload

# We render filter list after main table since after filter list is mounted we trigger request to
# populate table
ReactDOM.render JobBox.new(), document.getElementById("content")
ReactDOM.render FilterList.new(), document.getElementById("filters")
