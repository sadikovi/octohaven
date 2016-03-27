# Create View controller, examines content of the parent element on existence of the job data.
# If content exists and can be converted into json, everything is okay, otherwise report that job
# cannot be used as template.
class CreateController extends Reactable
  constructor: ->
    @state =
      name: "#{Namer.generate()}"
      cron: ""
      job: null
      submitted: false # whether or not controller has been submitted (restricts num of submissions)
      note_state: "" # validation state, either "loading", "success", or "error"
      note_message: "" # validation message
      submit_url: "/api/v1/timetable/create"

  getPayload: ->
    payload =
      name: @state.name
      cron: @state.cron
      job_uid: @state.job?.uid
    payload

  componentWillMount: ->
    data = Util.jsonOrElse(document.getElementById("job-content")?.innerHTML)
    @setState(job: data)
    emitter.on TIMETABLE_CREATE_NAME_CHANGED, (updatedName) =>
      @setState(name: updatedName)
    emitter.on TIMETABLE_CREATE_CRON_CHANGED, (updatedCron) =>
      @setState(cron: updatedCron)
    emitter.on TIMETABLE_CREATE_SUBMIT, =>
      Api.doPost @state.submit_url, {"Content-Type": "application/json"}, @getPayload(), =>
        @setState(submitted: true, note_state: "loading", note_message: "")
        console.debug "Submitting timetable", @getPayload()
      , (ok, json) =>
        if ok
          txt = "Timetable created. To resubmit the timetable, please refresh web-page"
          @setState(submitted: true, note_state: "success", note_message: "#{txt}")
          console.debug "Created new timetable", ok, json
        else
          txt = "Failed to create timetable, reason: #{json?.msg ? "unknown"}"
          @setState(submitted: false, note_state: "error", note_message: "#{txt}")
          console.error "Failed to create job", ok, json

  componentWillUnmount: ->
    emitter.off TIMETABLE_CREATE_NAME_CHANGED
    emitter.off TIMETABLE_CREATE_CRON_CHANGED

  render: ->
    if @state.job
      CreateView.new(@state)
    else
      @div({className: "blankslate"},
        @h1({className: "text-thin"}, "Could not load specified job"),
        @p({}, "Most likely specified job does not exist.")
        @p({}, "To create timetable, open 'Job details' page and click on 'Create timetable' " +
          "link in job actions. Start by selecting one from ", @a({href: "/jobs"}, "list of jobs")
        )
      )

class CreateView extends Reactable
  render: ->
    @div({},
      JobLink.new(job: @props.job),
      @div({className: "divider"}),
      TimetableName.new(name: @props.name),
      @div({className: "divider"}),
      CronExpression.new(cron: @props.cron),
      @div({className: "divider"}),
      ValidationPanel.new(note_state: @props.note_state, note_message: @props.note_message),
      ControlPanel.new(submitted: @props.submitted)
    )

class JobLink extends Reactable
  render: ->
    @div({className: "columns"},
      @div({className: "one-fourth column"},
        @span({className: "text-bold"}, "Job to use as template")
      ),
      @div({className: "three-fourths column"},
        @a({href: "#{@props.job.html_url}"}, "#{@props.job.name}")
      )
    )

class TimetableName extends Reactable
  handleInput: (event) ->
    emitter.emit TIMETABLE_CREATE_NAME_CHANGED, event.target.value
    console.debug "Emitted event", TIMETABLE_CREATE_NAME_CHANGED, event.target.value

  render: ->
    @div({className: "columns"},
      @div({className: "one-fourth column"},
        @span({className: "text-bold"}, "Timetable name")
      ),
      @div({className: "three-fourths column"},
        @input({type: "text", value: "#{@props.name}"
          , onChange: (event) => @handleInput(event)})
      )
    )

class CronExpression extends Reactable
  handleInput: (event) ->
    emitter.emit TIMETABLE_CREATE_CRON_CHANGED, event.target.value
    console.debug "Emitted event", TIMETABLE_CREATE_CRON_CHANGED, event.target.value

  render: ->
    @div({className: "columns"},
      @div({className: "one-fourth column"},
        @span({className: "text-bold"}, "Cron expression")
      ),
      @div({className: "three-fourths column"},
        @input({type: "text", className: "input-monospace", value: "#{@props.cron}"
          , onChange: (event) => @handleInput(event)})
      )
    )

class ValidationPanel extends Reactable
  render: ->
    if @props.note_state == "loading"
      @div({className: "loading segment"})
    else if @props.note_state == "success"
      @div({className: "success-box"}, "#{@props.note_message}")
    else if @props.note_state == "error"
      @div({className: "error-box"}, "#{@props.note_message}")
    else
      @div({className: "hidden segment"})

class ControlPanel extends Reactable
  showHelp: ->
    cronHelp = document.getElementById("cron-help")
    Util.removeClass(cronHelp, "hidden") if cronHelp

  handleSubmit: ->
    emitter.emit TIMETABLE_CREATE_SUBMIT
    console.debug "Emitted event", TIMETABLE_CREATE_SUBMIT

  render: ->
    disabled = if @props.submitted then "btn-disabled" else ""
    @div({className: "breadcrumb"},
      @div({className: "section"},
        @div({className: "btn btn-success #{disabled}", onClick: => @handleSubmit()}, "Submit")
      ),
      @div({className: "section"},
        @div({className: "btn", onClick: => @showHelp()}, "Show help")
      )
    )

ReactDOM.render CreateController.new(), document.getElementById("create-content")
