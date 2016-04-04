class LogController extends Reactable
  constructor: ->
    @state =
      status: null
      block: null
      page: null
      pages: null
      size: null
      prev_page_url: null
      next_page_url: null
      jump_to_page_url: null
      error: null

  fetchData: (url) ->
    Api.doGet url, null, null, null, (ok, json) =>
      if ok
        @setState(block: json.block, page: json.page, pages: json.pages, size: json.size
          , prev_page_url: json.prev_page_url, next_page_url: json.next_page_url
          , jump_to_page_url: json.jump_to_page_url, last_page_url: json.last_page_url, status: ok)
      else
        @setState(error: json?.msg, status: ok)

  componentWillMount: ->
    data = Util.jsonOrElse(document.getElementById("content-json")?.innerHTML)
    type = document.getElementById("content-type")?.innerHTML
    if data and (type.toLowerCase() == "stdout" or type.toLowerCase() == "stderr")
      url = if type.toLowerCase() == "stdout" then data.stdout_url else data.stderr_url
      @fetchData(url)

    emitter.on PAGE_INPUT_CHANGED, (value) =>
      @setState(page: value)
    emitter.on BLOCK_URL_UPDATED, (url) =>
      @fetchData(url)

  componentWillUnmount: ->
    emitter.off PAGE_INPUT_CHANGED

  render: ->
    if @state.status == null
      @div({className: "segments"})
    else if @state.status
      @div({className: "segments"},
        ControlPanel.new({prev_page_url: @state.prev_page_url, next_page_url: @state.next_page_url
          , jump_to_page_url: @state.jump_to_page_url, page: @state.page, pages: @state.pages
          , size: @state.size, last_page_url: @state.last_page_url}
        ),
        Container.new(block: @state.block)
      )
    else
      console.error "Error", @state.error, @state.status
      @div({className: "blankslate"},
        @h1({className: "text-thin"}, "Error occuried"),
        @p({}, "#{@state.error ? "Either log type of job is not recognized"}"),
        @p({}, "Check dev console for more info, or try reloading page")
      )

class ControlPanel extends Reactable
  load: (url) ->
    emitter.emit BLOCK_URL_UPDATED, url
    console.debug "Emitted event", BLOCK_URL_UPDATED, url, Date.now()

  jump: (url) ->
    @load(url.replace("_page_", @props.page))

  handleInput: (event) ->
    emitter.emit PAGE_INPUT_CHANGED, event.target.value
    console.debug "Emitted event", PAGE_INPUT_CHANGED, event.target.value, Date.now()

  render: ->
    @div({className: "segment"},
      @div({className: "breadcrumb"},
        @div({className: "section"},
          if @props.prev_page_url
            @div({className: "btn btn-compact", onClick: => @load(@props.prev_page_url)}, "Prev")
          else
            @div({className: "btn btn-compact btn-disabled"}, "Prev")
        ),
        @div({className: "section"},
          if @props.next_page_url
            @div({className: "btn btn-compact", onClick: => @load(@props.next_page_url)}, "Next")
          else
            @div({className: "btn btn-compact btn-disabled"}, "Next")
        ),
        @div({className: "section"},
          if @props.last_page_url
            @div({className: "btn btn-compact", onClick: => @load(@props.last_page_url)}, "Last")
          else
            @div({className: "btn btn-compact btn-disabled"}, "Last")
        ),
        @div({className: "separator"}, "|"),
        @div({className: "section"},
          @input({className: "input-squared", type: "text", value: "#{@props.page}"
            , onChange: (event) => @handleInput(event)})
        ),
        @div({className: "section"},
          if @props.jump_to_page_url
            @div({className: "btn btn-compact", onClick: => @jump(@props.jump_to_page_url)}, "Jump to page")
          else
            @div({className: "btn btn-compact btn-disabled"}, "Jump to page")
        ),
        @div({className: "separator"}, "|"),
        @div({className: "section"}, "Number of pages: #{@props.pages}"),
        @div({className: "section"}, "Block size: #{@props.size} bytes")
      )
    )

class Container extends Reactable
  render: ->
    @div({className: "segment"},
      @pre({className: "code-container"}, "#{@props.block}")
    )

ReactDOM.render LogController.new(), document.getElementById("content")
