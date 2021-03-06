# Job class to render the whole content segment
class JobController extends Reactable
  constructor: ->
    @state =
      job: null

  componentWillMount: ->
    data = Util.jsonOrElse(document.getElementById("content-json")?.innerHTML)
    @setState(job: data)
    # emit parsed job data to the job actions menu
    emitter.emit JOB_DATA_ARRIVED, data
    emitter.on JOB_CLOSED, (ok, json) =>
      @setState(job: json) if ok

  componentWillUnmount: ->
    emitter.off JOB_CLOSED

  render: ->
    JobView.new(data: @state.job)

class JobView extends Reactable
  convertTimestamp: (timestamp) ->
    if timestamp then Util.timestampToDate(timestamp) else ""

  timeDiff: (start, finish) ->
    if start and finish then Util.humanReadableDiff(finish - start) else ""

  render: ->
    if @props.data
      job = @props.data
      @div({className: "segments"},
        JobOption.new(name: "Job name (UID)", value: "#{job.name} (#{job.uid})"),
        JobOption.new(name: "Entrypoint", value: "#{job.entrypoint}"),
        JobOption.new(name: "Jar", value: "#{job.jar}"),
        StatusOption.new(name: "Status", value: "#{job.status}", url: job.close_url),
        JobOption.new(name: "Create time", value: "#{@convertTimestamp(job.createtime)}"),
        JobOption.new(name: "Submit time", value: "#{@convertTimestamp(job.submittime)}"),
        JobOption.new(name: "Start time", value: "#{@convertTimestamp(job.starttime)}"),
        JobOption.new(name: "Finish time, approx.", value: "#{@convertTimestamp(job.finishtime)}"),
        JobOption.new(name: "Elapsed time, approx.", value: "#{@timeDiff(job.starttime, job.finishtime)}"),
        JobOption.new(name: "Spark options", value: job.options, type: "dict"),
        JobOption.new(name: "Job options", value: job.jobconf, type: "array")
      )
    else
      @div({className: "blankslate"},
        @h1({className: "text-thin"}, "Could not load job")
        @p({}, "Make sure that provided job id exists or ",
          @a({href: "/jobs"}, "select one of the available jobs")
        )
      )

class JobOption extends Reactable
  render: ->
    @div({className: "segment"},
      @div({className: "columns"},
        @div({className: "one-fifth column"},
          @span({className: "text-bold"}, "#{@props.name}")
        ),
        @div({className: "four-fifths column"},
          if @props.type == "dict"
            # render dictionary value
            (@div({key: key}, "#{key} = #{value}") for key, value of @props.value)
          else if @props.type == "array"
            # render array value
            (@div({key: "#{elem}"}, "#{elem}") for elem in @props.value)
          else
            @span({className: @props.className}, "#{@props.value}")
        )
      )
    )

class StatusOption extends Reactable
  constructor: ->
    @state =
      enabled: true
      text: "Close"

  handleClick: (url) ->
    Api.doGet url, null, null, null, (ok, json) =>
      @setState(enabled: false, text: if ok then "Ok" else "Error")
      emitter.emit JOB_CLOSED, ok, json
      console.debug "Emitted event", JOB_CLOSED, ok, json

  render: ->
    @div({className: "segment"},
      @div({className: "columns"},
        @div({className: "one-fifth column"},
          @span({className: "text-bold"}, "#{@props.name}")
        ),
        @div({className: "four-fifths column"},
          @span({className: "#{statusLabel(@props.value)} medium margin-right"}, "#{@props.value}"),
          if @props.url
            @div({className: "btn btn-compact #{if !@state.enabled then "btn-disabled" else ""}"
              , onClick: => @handleClick(@props.url)}, "#{@state.text}")
          else
            @span()
        )
      )
    )

class JobActions extends Reactable
  constructor: ->
    @state =
      create_timetable_html_url: "#"
      view_stdout_html_url: "#"
      view_stderr_html_url: "#"

  componentWillMount: ->
    emitter.on JOB_DATA_ARRIVED, (job) =>
      @setState(create_timetable_html_url: "#{job.create_timetable_html_url}")
      @setState(view_stdout_html_url: "#{job.view_stdout_html_url}")
      @setState(view_stderr_html_url: "#{job.view_stderr_html_url}")

  componentWillUnmount: ->
    emitter.off JOB_DATA_ARRIVED

  render: ->
    @nav({className: "menu"},
      @div({className: "menu-heading"}, "Job actions"),
      @a({className: "menu-item", href: "#{@state.create_timetable_html_url}"},
        "Create timetable"),
      @a({className: "menu-item", href: "#{@state.view_stdout_html_url}"}, "View STDOUT"),
      @a({className: "menu-item", href: "#{@state.view_stderr_html_url}"}, "View STDERR"),
    )

ReactDOM.render JobActions.new(), document.getElementById("job-actions")
ReactDOM.render JobController.new(), document.getElementById("content")
