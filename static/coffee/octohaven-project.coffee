# add fast editor on description
project_name = ->
    a = document.getElementsByTagName("meta")
    return x.getAttribute("content") for x in a when x.name == "projectname"
project_hash = ->
    a = document.getElementsByTagName("meta")
    return x.getAttribute("content") for x in a when x.name == "projecthash"
# elements on page
## name
nameelem = document.getElementById "octohaven-project-desc"
## project - delete
deleteLink = document.getElementById "octohaven-project-action-delete"

unless nameelem
    throw new Error "Project name element is undefined"
nameeditor = new @FastEditor nameelem, (status, value) =>
    if status and value
        data =
            projectname: "#{@util.quote project_name()}"
            projectdesc: "#{@util.quote value}"
        @loader.sendrequest "post", "/api/project/update", {}, JSON.stringify(data)

@util.addEventListener deleteLink, "click", (e)=>
    e.preventDefault()
    # send request
    data =
        projectname: "#{@util.quote project_name()}"
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

# loading branches form
branchesform = document.getElementById "octohaven-branches-form"
brancheslist = document.getElementById "octohaven-branches-list"
branchesaddb = document.getElementById "octohaven-branches-addb"

unless branchesform and brancheslist and branchesaddb
    throw new Error "Branches form or its elements are undefined"

# no branches map
no_branches_map = () ->
    map =
        type: "div"
        cls: "blankslate"
        children: [
            header =
                type: "h1"
                cls: "text-thin"
                title: "No branches"
            paragraph =
                type: "p"
                cls: "text-mute"
                title: "Add one with [+ branch]"
        ]

# branches map
branches_map = (branches) ->
    _one_branch = (branch) ->
        if branch.default
            [default_t, delete_t] = ["DEFAULT", "---"]
        else
            [default_t, delete_t] = ["[ Set ]", "[ Delete ]"]
        # create maps
        _b_default =
            type: "a"
            href: ""
            title: "#{default_t}"
        _b_delete =
            type: "a"
            href: ""
            title: "#{delete_t}"
        # convert into elements
        _b_default = @mapper.parseMapForParent _b_default
        _b_default._branch = branch
        _b_delete = @mapper.parseMapForParent _b_delete
        _b_delete._branch = branch
        @util.addEventListener _b_default, "click", (e) -> e.preventDefault()
        if branch.default
            _b_default =
                type: "span"
                cls: "text-emphasized"
                title: "Default"
            _b_delete = null
        else
            @util.addEventListener _b_default, "click", (e) ->
                e.preventDefault()
                setDefault?(@_branch)
            @util.addEventListener _b_delete, "click", (e) ->
                e.preventDefault()
                deleteBranch?(@_branch)
        # overall branch map
        branch =
            type: "div"
            cls: "segment"
            children:
                type: "div"
                cls: "columns"
                children: [
                    name =
                        type: "div"
                        cls: "one-fifth column"
                        children:
                            type: "div"
                            cls: "segment"
                            children:
                                type: "a"
                                href: branch.link
                                title: branch.name
                    edited =
                        type: "div"
                        cls: "two-fifths column"
                        children:
                            type: "div"
                            cls: "segment"
                            title: convertTimeStampIntoRuntime?(branch.edited)
                    isdefault =
                        type: "div"
                        cls: "one-fifth column"
                        children:
                            type: "div"
                            cls: "segment"
                            children: [_b_default]
                    isdelete =
                        type: "div"
                        cls: "one-fifth column"
                        children:
                            type: "div"
                            cls: "segment"
                            children: [_b_delete]
                ]
    if branches and branches.length
        _branches_map =
            type: "div"
            cls: "segments"
            children: (_one_branch(x) for x in branches)
    else
        no_branches_map()

# error map
error_map = (msg) ->
    msg ?= "Cannot fetch branches."
    map =
        type: "div"
        cls: "blankslate"
        children: [
            header =
                type: "h1"
                cls: "text-thin"
                title: "Something went wrong"
            paragraph =
                type: "p"
                cls: "text-mute"
                title: "#{msg}"
            reload =
                type: "p"
                cls: "text-mute"
                children:
                    type: "a"
                    title: "Reload branches"
                    href: ""
                    onclick: (e) ->
                        reloadBranchesForm?()
                        e.preventDefault()
        ]

# send data and ask for branches initially
reloadBranchesForm = (link, data) ->
    data = data or {projectname: project_name(), branchname: "", projecthash: project_hash()}
    brancheslist.innerHTML = ""
    @util.addClass branchesform, "loading"
    link = link or "/api/branch/select"
    # send request
    @loader.sendrequest "post", link, {}, JSON.stringify(data)
    , (s, r) =>
        if s == 200
            r = JSON.parse r
            @mapper.parseMapForParent branches_map(r.data.branches), brancheslist
        else
            @mapper.parseMapForParent error_map(), brancheslist
        @util.removeClass branchesform, "loading"
    , (e, r) =>
        msg = JSON.parse(r).message if e == 400
        @mapper.parseMapForParent error_map(msg), brancheslist
        @util.removeClass branchesform, "loading"

createBranch = (branchname) ->
    reloadBranchesForm?("/api/branch/create",
        {projectname: project_name(), branchname: branchname, projecthash: project_hash()})

setDefault = (branch) ->
    reloadBranchesForm?("/api/branch/default",
        {projectname: project_name(), branchname: branch.name, projecthash: project_hash()})

deleteBranch = (branch) ->
    reloadBranchesForm?("/api/branch/delete",
        {projectname: project_name(), branchname: branch.name, projecthash: project_hash()})

convertTimeStampIntoRuntime = (timestamp) ->
    [now, date] = [new Date, new Date timestamp * 1000]
    diff = (now.getTime() - date.getTime())/1000.0
    if 0 < diff < 60
        # display seconds
        "Edited less than a minute ago"
    else if 60 <= diff < 60*60
        # display minutes
        "Edited #{Math.round diff/60} minutes ago"
    else if 60*60 <= diff < 24*60*60
        # display hours
        "Edited #{Math.round diff/60/60} hours ago"
    else
        # display full date
        "Edited on #{date.toLocaleString("en-nz")}"

# fire for the first time
reloadBranchesForm?()

# add fast editor on +branch
addbrancheditor = new @FastEditor branchesaddb, (status, value) ->
    createBranch?(value) if status
, "Create", "Cancel", "New branch name", false
