# add fast editor on description
projectid = ->
    a = document.getElementsByTagName("meta")
    return x.getAttribute("content") for x in a when x.name == "projectid"
# elements on page
## name
nameelem = document.getElementById "octohaven-project-name"
## project - delete
deleteLink = document.getElementById "octohaven-project-action-delete"

unless nameelem
    throw new Error "Project name element is undefined"
nameeditor = new @FastEditor nameelem, (status, value) =>
    if status and value and projectid
        @loader.sendrequest "get", "/api/project/update?id=#{projectid()}&name=#{@util.quote value}", {}, null, (s, r) ->
            console.log s, r
        , (e, r) ->
            console.log e, r

@util.addEventListener deleteLink, "click", (e)=>
    e.preventDefault()
    # send request
    data = {"projectid": "#{projectid()}"}
    @loader.sendrequest "post", "/api/project/delete", {}
    , JSON.stringify(data)
    , (s, r) =>
        if s == 200
            response = JSON.parse r
            [redirect, isdeleted] = [response.data.redirect, response.data.isdeleted]
            window.location.href = if redirect then redirect else "/"
        else
            console.log "General error happened due to project deletion"
    , (e, r) =>
        console.log "Error #{r}"
