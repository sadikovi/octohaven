_loader = @loader
_util = @util

class AbstractApi
    doRequest: (type, before, after, url, params) ->
        atype = type.toLowerCase()
        if params and atype == "get"
            url = url + "?" + ("#{_util.quote(k)}=#{_util.quote(v)}" for k, v of params).join("&")
            params = null
        else if atype == "post"
            params = JSON.stringify(params)
        before?()
        loader.sendrequest atype, url, {}, params
        , (success, response) ->
            json = util.jsonOrElse(response)
            after?(!!json, json)
        , (error, response) ->
            json = util.jsonOrElse(response)
            after?(false, json)

    doGet: (before, after, url, data=null) -> @doRequest("get", before, after, url, data)

    doPost: (before, after, url, data) -> @doRequest("post", before, after, url, data)

################################################################
### API
################################################################
# Status request. Fetches current status of server and Spark UI and Master URLs.
class StatusApi extends AbstractApi
    # Requests status from the server. Returns server status, UI and Master URL.
    # - before() -> function to run before sending request
    # - after(ok, json) -> function that will be called after response is received
    requestStatus: (before, after) -> @doGet(before, after, "/api/v1/spark/status", null)

@STATUS_API ?= new StatusApi

# File finder API
class FileApi extends AbstractApi
    ls: (before, after, url="/api/v1/finder/home") -> @doGet(before, after, url, null)

@FILE_API ?= new FileApi

class TemplateApi extends AbstractApi
    newTemplate: (name, template, before, after) ->
        data = name: "#{name}", content: template
        @doPost(before, after, "/api/v1/template/new", data)

@TEMPLATE_API ?= new TemplateApi
