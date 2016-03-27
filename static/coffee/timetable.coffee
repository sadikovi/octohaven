# Class to render the whole content segment
class TimetableController extends Reactable
  constructor: ->
    @state =
      timetable: null

  componentWillMount: ->
    data = Util.jsonOrElse(document.getElementById("content-json")?.innerHTML)
    @setState(timetable: data)
    emitter.on TIMETABLE_CANCELLED, (ok, json) =>
      @setState(timetable: json) if ok

  componentWillUnmount: ->
    emitter.off TIMETABLE_CANCELLED

  render: ->
    TimetableView.new(data: @state.timetable)

class TimetableView extends Reactable
  convertTimestamp: (timestamp) ->
    if timestamp then Util.timestampToDate(timestamp) else ""

  render: ->
    if @props.data
      timetable = @props.data
      @div({className: "segments"},
        TOption.new(name: "Timetable name (UID)", value: "#{timetable.name} (#{timetable.uid})"),
        StatusOption.new(name: "Status", value: "#{timetable.status}", url: timetable.cancel_url),
        TOption.new(name: "Create time", value: "#{@convertTimestamp(timetable.createtime)}"),
        TOption.new(name: "Cancel time", value: "#{@convertTimestamp(timetable.canceltime)}"),
        TOption.new(name: "Template job", value: "#{timetable.job?.name}", type: "href"
          , href: "#{timetable.job?.html_url}"),
        TOption.new(name: "Schedule", value: "#{timetable.cron?.pattern}"),
        TOption.new(name: "Number of scheduled jobs", value: "#{timetable.stats?.jobs}"),
        if timetable.stats?.last_time and timetable.stats?.last_job_html_url
          TOption.new(name: "Latest scheduled job", value: "#{Util.timestampToDate(timetable.stats.last_time)}"
            , type: "href", href: "#{timetable.stats.last_job_html_url}")
        else
          TOption.new(name: "Latest scheduled job", value: "hasn't happened yet")

      )
    else
      @div({className: "blankslate"},
        @h1({className: "text-thin"}, "Could not load timetable")
        @p({}, "Make sure that provided timetable id exists or ",
          @a({href: "/timetables"}, "select one of the available")
        )
      )

class TOption extends Reactable
  render: ->
    @div({className: "segment"},
      @div({className: "columns"},
        @div({className: "one-fifth column"},
          @span({className: "text-bold"}, "#{@props.name}")
        ),
        @div({className: "four-fifths column"},
          if @props.type == "href"
            @a({href: "#{@props.href}"}, "#{@props.value}")
          else
            @span({className: @props.className}, "#{@props.value}")
        )
      )
    )

class StatusOption extends Reactable
  constructor: ->
    @state =
      enabled: true
      text: "Cancel"

  handleClick: (url) ->
    Api.doGet url, null, null, null, (ok, json) =>
      @setState(enabled: false, text: if ok then "Ok" else "Error")
      emitter.emit TIMETABLE_CANCELLED, ok, json
      console.debug "Emitted event", TIMETABLE_CANCELLED, ok, json

  render: ->
    @div({className: "segment"},
      @div({className: "columns"},
        @div({className: "one-fifth column"},
          @span({className: "text-bold"}, "#{@props.name}")
        ),
        @div({className: "four-fifths column"},
          @span({className: "#{timetableStatusLabel(@props.value)} medium margin-right"},
            "#{@props.value}"),
          if @props.url
            @div({className: "btn btn-danger btn-compact #{if !@state.enabled then "btn-disabled" else ""}"
              , onClick: => @handleClick(@props.url)}, "#{@state.text}")
          else
            @span()
        )
      )
    )

ReactDOM.render TimetableController.new(), document.getElementById("content")
