# define dependencies
loader = @loader
util = @util

# Status request. Fetches current status of server and Spark UI and Master URLs.
class Status
    # constants for status
    @STATUS_PENDING = "Pending..."
    @STATUS_READY = "Server is ready"
    @STATUS_BUSY = "Server is busy"
    @STATUS_UNREACHABLE = "Server is unreachable"

    constructor: ->

    # Requests status from the server. Returns server status, UI and Master URL.
    # - before() -> function to run before sending request
    # - after(status, uiURL, masterURL) -> function that will be called after response is received
    requestStatus: (before, after) ->
        # call before function
        before?()
        # send request to find out status
        loader.sendrequest "get", "/api/v1/spark/status", {}, null
        , (code, response) =>
            json = util.jsonOrElse(response)
            if json
                data = json["content"]
                [status, uiAddress, masterAddress] = [data["status"],
                    data["spark-ui-address"], data["spark-master-address"]]
                after?(status, uiAddress, masterAddress)
            else
                after?(false, false, false)
        , (error, response) => after?(false, false, false)

# set class to be global
@Status ?= Status

# Filelist object as a helper to fetch breadcrumbs and files
class Filelist
    constructor: ->

    sendRequest: (url, before, after) ->
        before?()
        loader.sendrequest "get", url, {}, null
        , (code, response) =>
            json = util.jsonOrElse(response)
            if json then after?(true, json) else after?(false, json)
        , (error, response) =>
            json = util.jsonOrElse(response)
            after?(false, json)

    breadcrumbs: (directory, before, after) ->
        @sendRequest("/api/v1/file/breadcrumbs?path=#{util.quote(directory)}", before, after)

    # Files request
    files: (directory, before, after) ->
        @sendRequest("/api/v1/file/list?path=#{util.quote(directory)}", before, after)

# set class to be global
@Filelist ?= Filelist

# class to submit a job
class JobResolver
    constructor: ->

    submit: (data, before, after) ->
        before?()
        loader.sendrequest "post", "/api/v1/job/submit", {}, data
        , (code, response) =>
            json = util.jsonOrElse(response)
            if json then  after?(true, json) else after?(false, json)
        , (error, response) =>
            json = util.jsonOrElse(response)
            after?(false, json)

@JobResolver ?= JobResolver

# class to fetch jobs for a certain status and limit
class JobLoader
    constructor: ->

    get: (status, limit, before, after) ->
        before?()
        loader.sendrequest "get", "/api/v1/job/list?status=#{status}&limit=#{limit}", {}, null
        , (success, response) ->
            json = util.jsonOrElse(response)
            after?(!!json, json)
        , (error, response) ->
            json = util.jsonOrElse(response)
            after?(false, json)

    close: (jobid, before, after) ->
        before?()
        loader.sendrequest "get", "/api/v1/job/close?jobid=#{jobid}", {}, null
        , (success, response) ->
            json = util.jsonOrElse(response)
            after?(!!json, json)
        , (error, response) ->
            json = util.jsonOrElse(response)
            after?(false, json)

    getJob: (jobid, before, after) ->
        before?()
        loader.sendrequest "get", "/api/v1/job/get?jobid=#{jobid}", {}, null
        , (success, response) ->
            json = util.jsonOrElse(response)
            after?(!!json, json)
        , (error, response) ->
            json = util.jsonOrElse(response)
            after?(false, json)

@JobLoader ?= JobLoader

# loading templates
class TemplateLoader
    constructor: ->

    show: (before, after) ->
        before?()
        loader.sendrequest "get", "/api/v1/template/list", {}, null
        , (success, response) ->
            json = util.jsonOrElse(response)
            after?(!!json, json)
        , (error, response) ->
            json = util.jsonOrElse(response)
            after?(false, json)

    delete: (tid, before, after) ->
        before?()
        loader.sendrequest "get", "/api/v1/template/delete?templateid=#{tid}", {}, null
        , (success, response) ->
            json = util.jsonOrElse(response)
            after?(!!json, json)
        , (error, response) ->
            json = util.jsonOrElse(response)
            after?(false, json)

    create: (data, before, after) ->
        before?()
        loader.sendrequest "post", "/api/v1/template/create", {}, data
        , (success, response) ->
            json = util.jsonOrElse(response)
            after?(!!json, json)
        , (error, response) ->
            json = util.jsonOrElse(response)
            after?(false, json)

@TemplateLoader ?= TemplateLoader

# loading log blocks
class LogReader
    constructor: ->

    readFromStart: (jobid, type, page, before, after) ->
        before?()
        loader.sendrequest "get", "/api/v1/file/log?" +
            "jobid=#{util.quote(jobid)}&type=#{util.quote(type)}&page=#{util.quote(page)}", {}, null
        , (success, response) ->
            json = util.jsonOrElse(response)
            after?(!!json, json)
        , (error, response) ->
            json = util.jsonOrElse(response)
            after?(false, json)

@LogReader ?= LogReader
