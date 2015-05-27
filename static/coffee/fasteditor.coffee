class FastEditor
    constructor: (@elem, @onDidFinishEdit) ->
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
        @panel = new Panel value
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
        @assets.texter.textContent = value ? @panel.initvalue
        @panel = null
        @assets.trigger.style.display = ""
        @on = false

class Panel
    constructor: (@initvalue) ->
        @initvalue = if @initvalue then @initvalue.trim() else ""
        [@ok, @ko, @texter] = [@submit(), @cancel(), @input(@initvalue)]

    input: (value) ->
        i = document.createElement "input"
        [i.type, i.value] = ["text", "#{value}"]
        FastEditor._util.addClass i, "form-control", "short"
        i

    submit: ->
        s = document.createElement "div"
        s.innerHTML = "Save"
        FastEditor._util.addClass s, "btn", "btn-success"
        s

    cancel: ->
        c = document.createElement "div"
        c.innerHTML = "Cancel"
        FastEditor._util.addClass c, "btn"
        c

    html: ->
        main = document.createElement "div"
        FastEditor._util.addClass main, "ui horizontal list"
        # input section
        isec = document.createElement "div"
        FastEditor._util.addClass isec, "item"
        isec.appendChild @texter
        # submit section
        ssec = document.createElement "div"
        FastEditor._util.addClass ssec, "item"
        ssec.appendChild @ok
        # cancel section
        csec = document.createElement "div"
        FastEditor._util.addClass csec, "item"
        csec.appendChild @ko
        # append children
        main.appendChild isec
        main.appendChild ssec
        main.appendChild csec
        main

FastEditor._util = @util
@FastEditor ?= FastEditor
