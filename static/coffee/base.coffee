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

TIMETABLE_FILTER_SELECTED = "timetable-filter-selected"
TIMETABLE_ACTION_FIRED = "timetable-action-fired"
TIMETABLE_DATA_REQUESTED = "timetable-data-requested"
TIMETABLE_DATA_ARRIVED = "timetable-data-arrived"
TIMETABLE_CREATE_NAME_CHANGED = "timetable-create-name-changed"
TIMETABLE_CREATE_CRON_CHANGED = "timetable-create-cron-changed"
TIMETABLE_CREATE_SUBMIT = "timetable-create-submit"
TIMETABLE_CANCELLED = "timetable-cancelled"

BLOCK_ARRIVED = "block-arrived"
BLOCK_URL_UPDATED = "block-url-updated"
PAGE_INPUT_CHANGED = "page-input-changed"

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

  pre: (opts...) -> React.DOM.pre(opts...)

  small: (opts...) -> React.DOM.small(opts...)

  span: (opts...) -> React.DOM.span(opts...)

  textarea: (opts...) -> React.DOM.textarea(opts...)

  ul: (opts...) -> React.DOM.ul(opts...)

  @new: (props) ->
    @factory ?= React.createFactory(@)
    @factory(props)

# Job statuses
ALL = "ALL"
READY = "READY"
DELAYED = "DELAYED"
RUNNING = "RUNNING"
FINISHED = "FINISHED"
CLOSED = "CLOSED"
# List of statuses above
STATUS_LIST = [ALL, READY, DELAYED, RUNNING, FINISHED, CLOSED]
# Timetable statuses
TIMETABLE_ALL = "ALL"
TIMETABLE_ACTIVE = "ACTIVE"
TIMETABLE_PAUSED = "PAUSED"
TIMETABLE_CANCELLED = "CANCELLED"
# List of statuses above
TIMETABLE_STATUSES = [TIMETABLE_ALL, TIMETABLE_ACTIVE, TIMETABLE_PAUSED, TIMETABLE_CANCELLED]

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

# Timetable status function, returns class name for a status,
# so each status has different colour
timetableStatusLabel = (status) ->
  if status == TIMETABLE_ACTIVE
    "text-green"
  else if status == TIMETABLE_PAUSED
    "text-yellow"
  else if status == TIMETABLE_CANCELLED
    "text-red"
  else
    "text-mute"

# Shortcut for human readable difference
diff = (timestamp) -> Util.humanReadableTime(timestamp)
