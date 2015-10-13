class Util
    constructor: ->

    createElement: (tagname, id, cls, text, parent) ->
        return false unless tagname
        elem = document.createElement tagname
        elem.className = cls if cls
        elem.id = id if id
        elem.innerHTML = text if text
        parent.appendChild elem if parent
        return elem

    clear: (elem) -> elem.innerHTML = "" if elem

    addEventListener: (elem, event, handler) ->
        if elem.addEventListener
            elem.addEventListener event, handler, false
        else if elem.attachEvent
            elem.attachEvent 'on'+event, handler
        else
            elem['on'+event] = handler

    removeEventListener: (elem, event, handler) ->
        if elem.removeEventListener
            elem.removeEventListener event, handler, false
        else if elem.detachEvent
            elem.detachEvent('on'+event, handler)
        else
            elem['on'+event] = null

    addClass: (elem, classes...) ->
        c = elem.className.trim()
        c = if c then c.split ' ' else []
        m = c.concat (x for x in classes when x and x not in c)
        elem.className = m.join ' '

    removeClass: (elem, classes...) ->
        c = elem.className.split ' '
        elem.className = (x for x in c when x not in classes).join ' '

    hasClass: (elem, cls) ->
        return cls in elem.className.split ' '

    quote: (str) ->
        return encodeURIComponent(str).replace /[!'()*]/g, (c) ->
            return '%' + c.charCodeAt(0).toString(16)

    isArray: (obj) -> Array.isArray(obj) or {}.toString.call(obj) is '[object Array]'

    randomid: -> "#{Math.random()}".split(".")[1]

    # parses string into json and returns object, if okay, otherwise returns def
    jsonOrElse: (str, def=null) ->
        try
            obj = JSON.parse(str)
        catch e
            obj = def
        return obj

# init global util
@util ?= new Util
