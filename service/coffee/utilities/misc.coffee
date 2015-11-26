# miscellaneous functions that are used across all files

_mapper = @mapper
_util = @util
FastEditor = @FastEditor

class Misc
    blankslate: (internal) ->
        blankview = _mapper.parseMapForParent(type: "div", cls: "blankslate")
        _mapper.parseMapForParent(internal, blankview)
        blankview

    blankslateWithMsg: (header, msg) ->
        header = type: "h1", cls: "text-thin", title: "#{header}"
        body = type: "p", title: "#{msg}"
        @blankslate([header, body])

    segments: (content, parent = null) ->
        seg = type: "div", cls: "segments", children: content
        _mapper.parseMapForParent(seg, parent)

    segment: (content, parent = null) ->
        seg = type: "div", cls: "segment", children: content
        _mapper.parseMapForParent(seg, parent)

    columns: (content, parent = null) ->
        col = type: "div", cls: "columns", children: content
        _mapper.parseMapForParent(col, parent)

    section: (content, parent = null) ->
        sec = type: "div", cls: "section", children: content
        _mapper.parseMapForParent(sec, parent)

    jobOption: (name, desc, value, onValueChanged) ->
        # header with setting name and tooltip attached
        header = _mapper.parseMapForParent(
            type: "span", cls: "text-mute tooltipped tooltipped-n", title: "#{name}")
        header.setAttribute("aria-label", "#{desc}")
        header = _mapper.parseMapForParent(type: "div", cls: "one-fifth column", children: header)
        # trigger "Change"
        triggerLink = _mapper.parseMapForParent(type: "a", href: "", title: "Change")
        triggerLink.setAttribute("data-attr", "fast-editor-trigger")
        trigger = _mapper.parseMapForParent(type: "div", cls: "one-fifth column"
            , children: triggerLink)
        # value body
        body = _mapper.parseMapForParent(type: "div", cls: "three-fifths column", title: "#{value}")
        body.setAttribute("data-attr", "fast-editor-texter")
        # overall block of settings
        row = @segment(@columns([header, trigger, body]))
        row.setAttribute("data-attr", "fast-editor")
        # add fast editor
        new FastEditor(row, (status, value) -> onValueChanged?(status, value))
        # return row element
        return row

@misc ?= new Misc
