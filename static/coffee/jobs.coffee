# Building filters
class Filter extends Reactable
  render: ->
    tag = if @props.selected then "selected" else ""
    @li({className: "filter-item #{tag}", onClick: @props.onClick}, "#{@props.label}")

class FilterList extends Reactable
  constructor: ->
    @state =
      selected: ALL

  componentDidMount: ->
    @handleClick @state.selected

  handleClick: (status) ->
    @setState(selected: status)
    dispatcher.dispatch type: JOB_FILTER_SELECTED, data: status
    console.debug "Dispatched event: #{JOB_FILTER_SELECTED}", status, Date.now()

  filter: (status) ->
    func = => @handleClick(status)
    Filter.new(key: "#{status}", onClick: func, label: status, selected: status == @state.selected)

  render: ->
    @ul({className: "filter-list"}, (@filter(status) for status in STATUS_LIST))

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

  componentWillMount: ->
    emitter.on JOB_CLOSED_ARRIVED, (url, okay) =>
      @setState(clicked: true, txt: if okay then "Closed" else "Error") if url == @props.action

  handleClick: ->
    @setState(clicked: true)
    dispatcher.dispatch type: JOB_CLOSED, data: @props.action

  render: ->
    @div({className: "#{@props.className}"},
      if @props.action
        isOff = if @state.clicked then "btn-disabled" else ""
        @div({className: "btn btn-compact #{isOff}", onClick: (=> @handleClick())}, "#{@state.txt}")
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
      @xhr = Api.doGet(url, {status: status}, ->
        emitter.emit JOB_DATA_REQUESTED, status
        console.debug "Emitted event", JOB_DATA_REQUESTED, status, Date.now()
      , (okay, data) =>
        console.error "ERROR", data unless okay
        emitter.emit JOB_DATA_ARRIVED, okay, data?.rows
        console.debug "Emitted event", JOB_DATA_ARRIVED, okay, Date.now()
      )
    else if payload.type == JOB_CLOSED
      url = payload.data
      Api.doGet(url, null, null, (okay, data) =>
        console.error "ERROR", data unless okay
        emitter.emit JOB_CLOSED_ARRIVED, url, okay
        console.debug "Emitted event", JOB_CLOSED_ARRIVED, url, okay, Date.now()
      )
    else
      console.warn "Unrecognized dispatch object", payload

# We render filter list after main table since after filter list is mounted we trigger request to
# populate table
ReactDOM.render JobBox.new(), document.getElementById("content")
ReactDOM.render FilterList.new(), document.getElementById("status-filter")
