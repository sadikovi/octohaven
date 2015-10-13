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
        loader.sendrequest "get", "/api/v1/sparkstatus", {}, null
        , (code, response) =>
            json = util.jsonOrElse(response)
            if json
                data = json["content"]
                [status, uiAddress, masterAddress] = [data["sparkstatus"],
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
        @sendRequest("/api/v1/breadcrumbs?path=#{util.quote(directory)}", before, after)

    # Files request
    files: (directory, before, after) ->
        @sendRequest("/api/v1/list?path=#{util.quote(directory)}", before, after)

# set class to be global
@Filelist ?= Filelist

# class to submit a job
class JobResolver
    constructor: ->

    submit: (data, before, after) ->
        before?()
        loader.sendrequest "post", "/api/v1/submit", {}, data
        , (code, response) =>
            json = util.jsonOrElse(response)
            if json then  after?(true, json) else after?(false, json)
        , (error, response) =>
            json = util.jsonOrElse(response)
            after?(false, json)

@JobResolver ?= JobResolver
