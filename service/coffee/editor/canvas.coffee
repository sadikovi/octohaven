util = @util
mapper = @mapper

# base class
class Base
    constructor: (@body, @controls) -> @id = util.randomid()

class Canvas extends Base
    constructor: (@parent) ->
        unless @parent and @parent.nodeType == Node.ELEMENT_NODE
            throw new Error "Canvas parent should be ELEMENT_NODE"
        body = @_body @parent
        @divider = @_divider @parent
        controls = @_controls @parent
        # list for controls to keep track of
        @controlslist = {}
        # root module reference
        @root = null
        super body, controls

    # private init container method
    _body: (parent) ->
        map =
            type: "div"
            id: "octohaven-canvas-body"
            cls: "container"
        mapper.parseMapForParent map, parent

    _controls: (parent) ->
        container =
            type: "div"
            id: "octohaven-canvas-actions"
            cls: "container"
        container = mapper.parseMapForParent container, parent

        map =
            type: "div"
            cls: "breadcrumb"
        mapper.parseMapForParent map, container

    _divider: (parent) ->
        map =
            type: "div"
            cls: "divider"
        mapper.parseMapForParent map, parent

    addControl: (control) ->
        @controlslist[control.id] = control
        @controls.appendChild control.body
        mapper.parseMapForParent {type: "div", cls: "divider"}, @controls

    addModule: (module) ->
        return false unless module
        unless @root
            @root = module
        else
            node = @root
            while node.next
                node = node.next
            node.next = module
            module.previous = node
        @body.appendChild module.body

class Control extends Base
    # parent is one of the editor elements {Canvas, Module}
    constructor: (@name, @action) ->
        body = @_body()
        util.addEventListener body, "click", (e) => @action @
        super body

    _body: (parent) ->
        map =
            type: "div"
            cls: "btn"
            title: "#{@name}"
        mapper.parseMapForParent map, parent

class Module extends Base
    constructor: ->
        [@next, @previous] = [null, null]
        body = @_body()
        super body

    _body: ->
        map =
            type: "div"
            cls: "container"
            children: [
                top =
                    type: "div"
                    cls: "top attached tertiary segment"
                    title: "Top"
                bottom =
                    type: "div"
                    cls: "bottom attached segment medium fixed-height"
                    title: "Body"
            ]
        mapper.parseMapForParent map


@Canvas ?= Canvas
@Control ?= Control
@Module ?= Module
