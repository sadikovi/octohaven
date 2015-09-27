# form actions
class Form
    constructor: (@form, @onsubmit, @oncancel) ->
        unless @form and @hasDataAttribute @form, "form"
            throw new Error "Element is not a form"
        @assets = {}
        [@assets.controls, @assets.submit, @assets.cancel] = [[], null, null]
        # discover form
        @discoverPartial @form
        # state
        @ready = true
        # set onsubmit and oncancel
        if @assets.submit and @onsubmit
            Form._util.addEventListener @assets.submit, "click", (e) =>
                e.preventDefault()
                e.stopPropagation()
                @onsubmit @data()
        if @assets.cancel and @oncancel
            Form._util.addEventListener @assets.cancel, "click", (e) =>
                e.preventDefault()
                e.stopPropagation()
                @oncancel()

    hasDataAttribute: (elem, value) ->
        elem.hasAttribute("data-attr") and elem.getAttribute("data-attr") == value

    hasNameAttribute: (elem) -> elem.hasAttribute "data-name-attr"

    getNameAttribute: (elem) -> elem.getAttribute "data-name-attr"

    getControlForNameAttr: (name) ->
        for el in @assets.controls
            return el if @getNameAttribute(el) == name


    discoverPartial: (node) ->
         return false unless @assets and node and node.childNodes
         for elem in node.childNodes
             if elem and elem.nodeType == Node.ELEMENT_NODE
                 # check whether it is cancel or submit or control
                 if @hasDataAttribute(elem, "control") and @hasNameAttribute elem
                     # add to controls
                     @assets.controls.push(elem)
                 else if not @assets.submit and @hasDataAttribute elem, "submit"
                     @assets.submit = elem
                 else if not @assets.cancel and @hasDataAttribute elem, "cancel"
                     @assets.cancel = elem
                 else
                     @discoverPartial elem, @assets

    lock: ->
        # lock submit
        if @assets.submit
            @assets.submit.setAttribute "disabled", ""
            Form._util.addClass @assets.submit, "btn-disabled"
        # lock cancel
        if @assets.cancel
            @assets.cancel.setAttribute "disabled", ""
            Form._util.addClass @assets.cancel, "btn-disabled"
        # lock controls
        if @assets.controls and @assets.controls.length
            elem.setAttribute "disabled", "" for elem in @assets.controls


    unlock: ->
        # unlock submit
        if @assets.submit
            @assets.submit.removeAttribute "disabled"
            Form._util.removeClass @assets.submit, "btn-disabled"
        # unlock cancel
        if @assets.cancel
            @assets.cancel.removeAttribute "disabled", ""
            Form._util.removeClass @assets.cancel, "btn-disabled"
        # unlock controls
        if @assets.controls
            elem.removeAttribute "disabled", "" for elem in @assets.controls

    startLoading: ->
        return false unless @ready
        @ready = false
        @lock()
        Form._util.addClass @form, "loading"

    stopLoading: ->
        return false if @ready
        @unlock()
        Form._util.removeClass @form, "loading"
        @ready = true

    data: ->
        info = {}
        info["#{@getNameAttribute(elem)}"] = elem.value for elem in @assets.controls
        info

    createMessage: (type, header, message) ->
        mainElem = document.createElement "div"
        if type == "success"
            Form._util.addClass mainElem, "#{type}", "success-box"
        else
            Form._util.addClass mainElem, "#{type}", "error-box"
        # header
        headerElem = document.createElement "h4"
        headerElem.innerHTML = "#{header}"
        # paragraph
        paragElem = document.createElement "p"
        paragElem.innerHTML = "#{message}"
        # append children
        mainElem.appendChild headerElem
        mainElem.appendChild paragElem
        # return mainElem
        mainElem

    destroyMessage: ->
        if @message
            @message.remove()
            @message = null

    appendMessage: ->
        return false unless @form and @message
        if @form.firstChild
            @form.insertBefore @message, @form.firstChild
        else
            @form.appendChild @message

    showErrorMessage: (msg) ->
        @destroyMessage()
        @message = @createMessage "error", "KO", msg
        @appendMessage()

    showSuccessMessage: (msg) ->
        @destroyMessage()
        @message = @createMessage "success", "OK", msg
        @appendMessage()


Form._util = @util
@Form ?= Form
