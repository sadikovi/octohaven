newProjectForm = document.getElementById "new-project-form"

unless newProjectForm
    throw new Error("Form is undefined")

# actions
createbtn =
    type: "button"
    cls: "btn btn-success"
    title: "Create"
createbtn = @mapper.parseMapForParent createbtn

cancelbtn =
    type: "button"
    cls: "btn"
    title: "Cancel"
cancelbtn = @mapper.parseMapForParent cancelbtn

# project id
idinput =
    type: "input"
    inputtype: "text"
    cls: "input-block input-contrast"
    placeholder: "Project id"
idinput = @mapper.parseMapForParent idinput

idmsg =
    type: "p"
    cls: "note"
idmsg = @mapper.parseMapForParent idmsg

iddl =
    type: "dl"
    cls: "form required"
    children: [
        dt =
            type: "dt"
            children:
                type: "label"
                title: "Project id"
        dd =
            type: "dd"
            children: [idinput]
        msg =
            type: "div"
            children: [idmsg]
    ]
iddl = @mapper.parseMapForParent iddl

# project name
nameinput =
    type: "input"
    cls: "input-block input-contrast"
    inputtype: "text"
    placeholder: "Project name"
nameinput = @mapper.parseMapForParent nameinput

namedl =
    type: "dl"
    cls: "form"
    children: [
        dt =
            type: "dt"
            children:
                type: "label"
                title: "Project name / description"
        dd =
            type: "dd"
            children: [nameinput]
    ]
namedl = @mapper.parseMapForParent namedl

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

randomlink =
    type: "a"
    href: ""
    title: "#{generate()}"
    onclick: (e)=>
        idinput.value = randomlink.innerHTML
        checkvalue iddl, idinput, idmsg
        e.stopPropagation()
        e.preventDefault()
randomlink = @mapper.parseMapForParent randomlink

generatelink =
    type: "a"
    href: ""
    title: "another one"
    onclick: (e)=>
        randomlink.innerHTML = generate()
        e.stopPropagation()
        e.preventDefault()
generatelink = @mapper.parseMapForParent generatelink

# main map
map = [
    iddl
    note =
        type: "dl"
        cls: "form-note"
        children:
            type: "p"
            cls: "note"
            children: [
                first =
                    type: "span"
                    title: "Don't know what unique name to pick? Try "
                randomlink
                second =
                    type: "span"
                    title: " or get "
                generatelink
            ]
    namedl
    actions =
        type: "dl"
        cls: "form"
        children:
            type: "dl"
            cls: "form-actions"
            children: [createbtn, cancelbtn]
]
@mapper.parseMapForParent map, newProjectForm

changeState = (dl, input, p, status, msg) ->
    [success, successful, successlbl] = ["success", "successful", "text-green"]
    [error, errored, errorlbl] = ["error", "errored", "text-red"]
    # clear
    @util.removeClass dl, errored, successful
    @util.removeClass input, error, success
    @util.removeClass(p, errorlbl, successlbl) if p
    p.innerHTML = "" if p

    if status == "success"
        @util.addClass dl, successful
        @util.addClass input, success
        if p and msg
            @util.addClass p, successlbl
            p.innerHTML = "#{msg}"
    else if status == "error"
        @util.addClass dl, errored
        @util.addClass input, error
        if p and msg
            @util.addClass p, errorlbl
            p.innerHTML = "#{msg}"

checkvalue = (dl, input, p) ->
    value = input.value
    # reset state
    changeState dl, input, p, "reset"
    # make api call
    return false unless value
    result = value.length > 3 and /^[\w-]+$/i.test(value)
    if result
        changeState dl, input, p, "success", "All good"
    else
        changeState dl, input, p, "error", "Some error"

@util.addEventListener idinput, "keyup", (e)=> checkvalue iddl, idinput, idmsg
@util.addEventListener idinput, "onchange", (e)=> checkvalue iddl, idinput, idmsg
@util.addEventListener idinput, "onpaste", (e)=> checkvalue iddl, idinput, idmsg
