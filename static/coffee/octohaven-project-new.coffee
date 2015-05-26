# get form element
theFormElem = document.getElementById "octohaven-new-project-form"
# get form object
theForm = new @Form theFormElem, (data) =>
    theForm.destroyMessage()
    theForm.startLoading()
    # quote string data
    data[k] = @util.quote v for k, v of data
    # send request
    @loader.sendrequest "post", "/api/project/new"
    , {}
    , JSON.stringify(data)
    , (success, response) =>
        theForm.stopLoading()
        if success == 200
            response = JSON.parse response
            [redirect, isnew] = [response.data.redirect, response.data.isnew]
            if redirect
                window.location.href = redirect
            else
                theForm.showSuccessMessage response.message
        else
            theForm.showErrorMessage "Something unexpected happened"
        # window.location.href = "/project/old"
    , (error, response) =>
        theForm.stopLoading()
        try
            response = JSON.parse response
            theForm.showErrorMessage response.message
        catch
            theForm.showErrorMessage "Something unexpected happened"

# find project id input
projectidInput = theForm.getControlForNameAttr "projectid"
throw new Error("Project id field is not found") unless projectidInput

# random id generator
generate = ->
    adjs = [
        "autumn", "hidden", "bitter", "misty", "silent", "empty", "dry", "dark",
        "summer", "icy", "delicate", "quiet", "white", "cool", "spring", "winter",
        "patient", "twilight", "dawn", "crimson", "wispy", "weathered", "blue",
        "billowing", "broken", "cold", "damp", "falling", "frosty", "green",
        "long", "late", "lingering", "bold", "little", "morning", "muddy", "old",
        "red", "rough", "still", "small", "sparkling", "throbbing", "shy",
        "wandering", "withered", "wild", "black", "young", "holy", "solitary",
        "fragrant", "aged", "snowy", "proud", "floral", "restless", "divine",
        "polished", "ancient", "purple", "lively", "nameless"
    ]
    nouns = [
        "waterfall", "river", "breeze", "moon", "rain", "wind", "sea", "morning",
        "snow", "lake", "sunset", "pine", "shadow", "leaf", "dawn", "glitter",
        "forest", "hill", "cloud", "meadow", "sun", "glade", "bird", "brook",
        "butterfly", "bush", "dew", "dust", "field", "fire", "flower", "firefly",
        "feather", "grass", "haze", "mountain", "night", "pond", "darkness",
        "snowflake", "silence", "sound", "sky", "shape", "surf", "thunder",
        "violet", "water", "wildflower", "wave", "water", "resonance", "sun",
        "wood", "dream", "cherry", "tree", "fog", "frost", "voice", "paper",
        "frog", "smoke", "star"
    ]

    rnd = Math.floor(Math.random() * Math.pow(2, 12))
    "#{adjs[rnd>>6%64]}-#{nouns[rnd%64]}"

# activate random id generator
randomlink = document.getElementById "form-random-projectid"
randomlink.innerHTML = generate()
generatelink = document.getElementById "form-generate-projectid"
@util.addEventListener randomlink, "click", (e)=>
    projectidInput.value = randomlink.innerHTML
    if document.createEvent
        event = document.createEvent "HTMLEvents"
        event.initEvent "keyup", true, true
        projectidInput.dispatchEvent event
    else
        event = document.createEventObject()
        event.eventType = "keyup"
        projectidInput.fireEvent "on#{event.eventType}", event

    e.preventDefault()
    e.stopPropagation()

@util.addEventListener generatelink, "click", (e)=>
    randomlink.innerHTML = generate()
    e.preventDefault()
    e.stopPropagation()

# check state real-time
changeState = (input, status) ->
    [error, success] = ["control-errored", "control-successful"]
    @util.removeClass input, error, success
    if status == "success"
        @util.addClass input, success
    else if status == "error"
        @util.addClass input, error

checkvalue = (value, ok, ko) ->
    # make api call
    value = @util.quote value
    @loader.sendrequest "get", "/api/project/validate?id=#{value}", {}, null, (status, res)=>
        (if status == 200 then ok?() else ko?())
    , (status, res)=>
        ko?()

# default state
changeState projectidInput

# assign actions
@util.addEventListener projectidInput, "keyup", (e)=>
    checkvalue e.target.value, (=> changeState e.target, "success"), (=> changeState e.target, "error")

@util.addEventListener projectidInput, "onchange", (e)=>
    checkvalue e.target.value, (=> changeState e.target, "success"), (=> changeState e.target, "error")

@util.addEventListener projectidInput, "onpaste", (e)=>
    checkvalue e.target.value, (=> changeState e.target, "success"), (=> changeState e.target, "error")
