class FastEditor
    constructor: (@elem, @onDidFinishEdit, @oktext="Save", @canceltext="Cancel", @placeholder="", @displayvalue=true) ->
        # fast-editor
        # fast-editor-trigger
        unless @elem and @elem.nodeType == Node.ELEMENT_NODE and @hasDataAttribute @elem
            throw new Error "Wrong element"
        @assets = {}
        [@assets.texter, @assets.trigger] = [null, null]
        # search for components
        @discover @elem
        unless @assets.texter and @assets.trigger
            throw new Error "Insufficient structure"
        FastEditor._util.addEventListener @assets.trigger, "click", (e)=>
            @showPanel()
            e.preventDefault()
        @on = false

    getAttribute: (elem) -> elem.getAttribute "data-attr"

    hasDataAttribute: (elem) -> @getAttribute(elem) == "fast-editor"

    hasTriggerAttribute: (elem) -> @getAttribute(elem) == "fast-editor-trigger"

    hasTextAttribute: (elem) -> @getAttribute(elem) == "fast-editor-texter"

    discover: (node) ->
        return false unless node and node.childNodes
        for elem in node.childNodes
            if elem and elem.nodeType == Node.ELEMENT_NODE
                # check whether it is cancel or submit or control
                if @hasTriggerAttribute elem
                    @assets.trigger = elem
                else if @hasTextAttribute elem
                    @assets.texter = elem
                else
                    @discover elem

    showPanel: (value) ->
        return false if @on
        value = value or "#{@assets.texter.textContent}"
        @panel = new Panel value, @placeholder, @oktext, @canceltext
        @assets.texter.innerHTML = ""
        @assets.texter.appendChild @panel.html()
        # hide trigger
        @assets.trigger.style.display = "none"
        # assign actions
        FastEditor._util.addEventListener @panel.ok, "click", (e)=>
            text = @panel.texter.value
            @hidePanel? text
            @onDidFinishEdit? true, text
            e.preventDefault()
        FastEditor._util.addEventListener @panel.ko, "click", (e)=>
            @hidePanel?()
            @onDidFinishEdit? false
            e.preventDefault()
        @on = true

    hidePanel: (value) ->
        return false unless @on
        @assets.texter.textContent = (if @displayvalue then value else null) ? @panel.initvalue
        @panel = null
        @assets.trigger.style.display = ""
        @on = false

class Panel
    constructor: (@initvalue, @placeholder="", @oktext="Save", @canceltext="Cancel") ->
        @initvalue = if @initvalue then @initvalue.trim() else ""
        [@ok, @ko, @texter] = [@submit(), @cancel(), @input(@initvalue)]

    input: (value) ->
        i = document.createElement "input"
        i.setAttribute "placeholder", "#{@placeholder}"
        [i.type, i.value] = ["text", "#{value}"]
        FastEditor._util.addClass i, "form-control", "short"
        i

    submit: ->
        s = document.createElement "div"
        s.innerHTML = "#{@oktext}"
        FastEditor._util.addClass s, "btn", "btn-success"
        s

    cancel: ->
        c = document.createElement "div"
        c.innerHTML = "#{@canceltext}"
        FastEditor._util.addClass c, "btn"
        c

    html: ->
        main = document.createElement "div"
        FastEditor._util.addClass main, "breadcrumb"
        # input section
        isec = document.createElement "div"
        FastEditor._util.addClass isec, "section"
        isec.appendChild @texter
        # submit section
        ssec = document.createElement "div"
        FastEditor._util.addClass ssec, "section"
        ssec.appendChild @ok
        # cancel section
        csec = document.createElement "div"
        FastEditor._util.addClass csec, "section"
        csec.appendChild @ko
        # divider
        _divider = ->
            divider = document.createElement "div"
            FastEditor._util.addClass divider, "separator"
            divider
        # append children
        main.appendChild k for k in [isec, _divider(), ssec, _divider(), csec]
        main

FastEditor._util = @util
@FastEditor ?= FastEditor
