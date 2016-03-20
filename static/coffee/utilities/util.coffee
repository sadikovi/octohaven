class Util
  @createElement: (tagname, id, cls, text, parent) ->
    return false unless tagname
    elem = document.createElement tagname
    elem.className = cls if cls
    elem.id = id if id
    elem.innerHTML = text if text
    parent.appendChild elem if parent
    return elem

  @clear: (elem) -> elem.innerHTML = "" if elem

  @addEventListener: (elem, event, handler) ->
    if elem.addEventListener
      elem.addEventListener event, handler, false
    else if elem.attachEvent
      elem.attachEvent 'on'+event, handler
    else
      elem['on'+event] = handler

  @removeEventListener: (elem, event, handler) ->
    if elem.removeEventListener
      elem.removeEventListener event, handler, false
    else if elem.detachEvent
      elem.detachEvent('on'+event, handler)
    else
      elem['on'+event] = null

  @addClass: (elem, classes...) ->
    c = elem.className.trim()
    c = if c then c.split ' ' else []
    m = c.concat (x for x in classes when x and x not in c)
    elem.className = m.join ' '

  @removeClass: (elem, classes...) ->
    c = elem.className.split ' '
    elem.className = (x for x in c when x not in classes).join ' '

  @hasClass: (elem, cls) ->
    return cls in elem.className.split ' '

  @quote: (str) ->
    return encodeURIComponent(str).replace /[!'()*]/g, (c) ->
      return '%' + c.charCodeAt(0).toString(16)

  @unquote: (str) -> return decodeURIComponent(str)

  @isArray: (obj) -> Array.isArray(obj) or {}.toString.call(obj) is '[object Array]'

  @randomid: -> "#{Math.random()}".split(".")[1]

  # Parse string into json and returns object, if okay, otherwise returns default value
  @jsonOrElse: (str, def=null) ->
    try
      obj = JSON.parse(str)
    catch e
      obj = def
    return obj

  # Parse integer, if fails returns default
  @intOrElse: (int, def=-1) ->
    a = parseInt(int, 10)
    return if a != NaN then a else def

  @humanReadableTime: (timestamp, locale="en-nz") ->
    [now, date] = [new Date, new Date timestamp]
    diff = (now.getTime() - date.getTime()) / 1000.0
    if 0 < diff < 60
      # Display seconds
      "less than a minute ago"
    else if 60 <= diff < 60*60
      # Display minutes
      "#{Math.floor diff/60} minutes ago"
    else if 60*60 <= diff < 24*60*60
      # Display hours
      "#{Math.floor diff/60/60} hours ago"
    else
      # Display full date
      "#{date.toLocaleString(locale)}"

  @timestampToDate: (timestamp, locale="en-nz") ->
    date = new Date timestamp
    "#{date.toLocaleString(locale)}"

  # Show time difference nicely, e.g. 10min. Difference in milliseconds
  @humanReadableDiff: (diff) ->
    seconds = Math.floor(diff / 1000)
    hours = Math.floor(seconds / 3600)
    minutes = Math.floor(seconds / 60)
    if hours > 0
      # display hours and minutes
      "#{hours}hrs #{minutes % 60}min"
    else if minutes > 0
      # display minutes and seconds
      "#{minutes}min #{seconds % 60}sec"
    else
      # display seconds
      "#{seconds}sec (#{diff})"

  # Return map of parameters from search string (window.location)
  @windowParameters: ->
    unless window and window.location and window.location.search
      throw new Error("Window.location is not set properly")
    searchstr = window.location.search?.trim()
    arr = (component.split("=", 2) for component in searchstr.split("&"))
    # Unquote keys and values
    dict = {}
    for elem in arr
      str = if elem[0].indexOf("?") == 0 then elem[0].substring(1) else elem[0]
      key = @unquote(str)
      value = if elem[1] then @unquote(elem[1]) else null
      dict[key] = value
    dict
