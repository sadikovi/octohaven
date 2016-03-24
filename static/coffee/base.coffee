# Creating dispatcher for application
dispatcher = new Flux.Dispatcher

# Creating emitter for application
emitter = new EventEmitter

# List of events in application
JOB_FILTER_SELECTED = "job-filter-selected"
JOB_DATA_REQUESTED = "job-data-requested"
JOB_DATA_ARRIVED = "job-data-arrived"

JOB_CLOSED = "job-closed"
JOB_CLOSED_ARRIVED = "job-closed-arrived"

OPTION_CHANGED = "option-changed"

FINDER_ELEM_CLICKED = "finder-elem-clicked"
FINDER_JAR_SELECTED = "finder-jar-selected"

JOB_SUBMIT_REQUESTED = "job-submit-requested"

TEMPLATE_DELETED = "template-deleted"
TEMPLATE_LOADING = "template-loading"
TEMPLATE_SAVING = "template-saving"
TEMPLATE_SAVED = "template-saved"

# React base class for CoffeeScript
class Reactable extends React.Component
  constructor: (props) ->
    super props

  render: ->

  a: (opts...) -> React.DOM.a(opts...)

  div: (opts...) -> React.DOM.div(opts...)

  h1: (opts...) -> React.DOM.h1(opts...)

  h2: (opts...) -> React.DOM.h2(opts...)

  input: (opts...) -> React.DOM.input(opts...)

  li: (opts...) -> React.DOM.li(opts...)

  nav: (opts...) -> React.DOM.nav(opts...)

  p: (opts...) -> React.DOM.p(opts...)

  small: (opts...) -> React.DOM.small(opts...)

  span: (opts...) -> React.DOM.span(opts...)

  textarea: (opts...) -> React.DOM.textarea(opts...)

  ul: (opts...) -> React.DOM.ul(opts...)

  @new: (props) ->
    @factory ?= React.createFactory(@)
    @factory(props)

# Job statuses
READY = "READY"
DELAYED = "DELAYED"
RUNNING = "RUNNING"
FINISHED = "FINISHED"
CLOSED = "CLOSED"
ALL = "ALL"
# List of statuses above
STATUS_LIST = [ALL, READY, DELAYED, RUNNING, FINISHED, CLOSED]

# Job status function, returns different class name for each status
# Used to label elements
statusLabel = (status) ->
  if status == READY
    "text-green"
  else if status == DELAYED
    "text-yellow"
  else if status == RUNNING
    "text-orange"
  else if status == FINISHED
    "text-teal"
  else if status == CLOSED
    "text-mute"
  else
    "text-mute"

# Shortcut for human readable difference
diff = (timestamp) -> Util.humanReadableTime(timestamp)
