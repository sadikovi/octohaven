class Loader
  # Requests are always asynchronous
  # method -> post or get
  # url
  # headers -> an object {key1: value1, key2: value2}
  # payload -> data to send
  # success -> function called when response is OK
  # error -> function called when response is KO
  @sendrequest: (method, url, headers, payload, success, error) ->
    xmlhttp = if window.XMLHttpRequest then new XMLHttpRequest else new ActiveXObject "Microsoft.XMLHTTP"
    # Set state change function
    xmlhttp.onreadystatechange= ->
      if xmlhttp.readyState is 4
        if 200 <= xmlhttp.status < 300
          success? xmlhttp.status, xmlhttp.responseText
        else
          error? xmlhttp.status, xmlhttp.responseText
    # Prepare and send request (always async)
    xmlhttp.open method, url, true
    for key, value of headers
      xmlhttp.setRequestHeader key, value
    xmlhttp.send(payload)
    xmlhttp

  # Sync request (no callback)
  @syncrequest: (method, url, headers, payload) ->
    xmlhttp = if window.XMLHttpRequest then new XMLHttpRequest else new ActiveXObject "Microsoft.XMLHTTP"
    xmlhttp.open method, url, false
    for key, value of headers
      xmlhttp.setRequestHeader key, value
    xmlhttp.send(payload)
    xmlhttp
