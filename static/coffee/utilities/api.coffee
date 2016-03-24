# Abstract API class as a wrapper on Loader
class Api
    @doRequest: (type, url, headers, params, before, after) ->
        atype = type.toLowerCase()
        if params and atype == "get"
            url = url + "?" + ("#{Util.quote(k)}=#{Util.quote(v)}" for k, v of params).join("&")
            params = null
        else if atype == "post"
            params = JSON.stringify(params)
        before?()
        Loader.sendrequest atype, url, headers, params
        , (success, response) ->
            json = Util.jsonOrElse(response)
            after?(!!json, json)
        , (error, response) ->
            json = Util.jsonOrElse(response)
            after?(false, json)

    @doGet: (url, headers={}, data=null, before, after) ->
      @doRequest("get", url, headers, data, before, after)

    @doPost: (url, headers={}, data, before, after) ->
      @doRequest("post", url, headers, data, before, after)
