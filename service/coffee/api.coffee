# define dependencies
loader = @loader

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
            if code == 200
                json = JSON.parse response
                status = json["content"]["sparkstatus"]
                uiAddress = json["content"]["spark-ui-address"]
                masterAddress = json["content"]["spark-master-address"]
                after?(status, uiAddress, masterAddress)
            else
                # report error at this stage
                console.log "[ERROR] #{response}"
                after?(false, false, false)
        , (error, response) =>
            console.log "[ERROR] #{response}"
            after?(false, false, false)

# set class to be global
@Status ?= Status

# Filelist object as a helper to fetch breadcrumbs and files
class Filelist
    constructor: ->

    # Breadcrumbs api requester.
    # - before() -> function to run before sending request
    # - after(status, uiURL, masterURL) -> function that will be called after response is received
    sendRequest: (url, before, after) ->
        before?()
        loader.sendrequest "get", url, {}, null
        , (code, response) =>
            if code == 200
                json = JSON.parse response
                console.log(json)
                after?(json)
            else
                console.log "[ERROR] #{response}"
                after?(false)
        , (error, response) =>
            console.log "[ERROR] #{response}"
            after?(false)

    breadcrumbs: (directory, before, after) ->
        @sendRequest("/api/v1/breadcrumbs?path=#{directory}", before, after)

    # Files request
    files: (directory, before, after) ->
        @sendRequest("/api/v1/list?path=#{directory}", before, after)

# set class to be global
@Filelist ?= Filelist
