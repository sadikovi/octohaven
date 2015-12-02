_loader = @loader
_util = @util

class AbstractApi
    doRequest: (type, before, after, url, data) ->
        atype = type.toLowerCase()
        # construct key-value pairs, quote them
        params = {}
        params[_util.quote(k)] = _util.quote(v) for k, v of data if data
        if params and atype == "get"
            url = url + "?" + ("#{k}=#{v}" for k, v of params).join("&")
            params = null
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

@StatusApi ?= StatusApi

# Filelist object as a helper to fetch breadcrumbs and files
class FilelistApi extends AbstractApi
    breadcrumbs: (directory, before, after) ->
        @doGet(before, after, "/api/v1/file/breadcrumbs", {path: "#{directory}"})

    files: (directory, before, after) ->
        @doGet(before, after, "/api/v1/file/list", {path: directory})

@FilelistApi ?= FilelistApi

# class to fetch jobs for a certain status and limit, create or cancel jobs
class JobApi extends AbstractApi
    get: (status, limit, before, after) ->
        params = status: "#{status}", limit: "#{limit}"
        @doGet(before, after, "/api/v1/job/list", params)

    close: (id, before, after) -> @doGet(before, after, "/api/v1/job/close", {jobid: "#{id}"})

    getJob: (id, before, after) -> @doGet(before, after, "/api/v1/job/get", {jobid: "#{id}"})

    submit: (data, before, after) -> @doPost(before, after, "/api/v1/job/submit", data)

@JobApi ?= JobApi


# loading templates
class TemplateApi extends AbstractApi
    show: (before, after) -> @doGet(before, after, "/api/v1/template/list")

    delete: (id, before, after) ->
        @doGet(before, after, "/api/v1/template/delete", {templateid: "#{id}"})

    create: (data, before, after) -> @doPost(before, after, "/api/v1/template/create", data)

@TemplateApi ?= TemplateApi

# loading log blocks
class LogApi extends AbstractApi
    readFromStart: (jobid, type, page, before, after) ->
        params = jobid: "#{jobid}", type: "#{type}", page: "#{page}"
        @doGet(before, after, "/api/v1/file/log", params)

@LogApi ?= LogApi

# Timetable API to submit, fetch, reset timetables
class TimetableApi extends AbstractApi
    submit: (data, before, after) -> @doPost(before, after, "/api/v1/timetable/create", data)

    list: (includeJobs, statuses, before, after) ->
        params = includejobs: "#{includeJobs}", status: "#{statuses}"
        @doGet(before, after, "/api/v1/timetable/list", params)

    get: (id, before, after) -> @doGet(before, after, "/api/v1/timetable/get", {id: "#{id}"})

    pause: (id, before, after) -> @doGet(before, after, "/api/v1/timetable/pause", {id: "#{id}"})

    resume: (id, before, after) -> @doGet(before, after, "/api/v1/timetable/resume", {id: "#{id}"})

    cancel: (id, before, after) -> @doGet(before, after, "/api/v1/timetable/cancel", {id: "#{id}"})

@TimetableApi ?= TimetableApi
