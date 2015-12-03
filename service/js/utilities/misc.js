(function() {
  var Misc, _FastEditor, _mapper, _util;

  _mapper = this.mapper;

  _util = this.util;

  _FastEditor = this.FastEditor;

  Misc = (function() {
    function Misc() {}

    Misc.prototype.blankslate = function(internal) {
      var blankview;
      blankview = _mapper.parseMapForParent({
        type: "div",
        cls: "blankslate"
      });
      _mapper.parseMapForParent(internal, blankview);
      return blankview;
    };

    Misc.prototype.blankslateWithMsg = function(header, msg) {
      var body;
      header = {
        type: "h1",
        cls: "text-thin",
        title: "" + header
      };
      body = {
        type: "p",
        title: "" + msg
      };
      return this.blankslate([header, body]);
    };

    Misc.prototype.segments = function(content, parent) {
      var seg;
      if (parent == null) {
        parent = null;
      }
      seg = {
        type: "div",
        cls: "segments",
        children: content
      };
      return _mapper.parseMapForParent(seg, parent);
    };

    Misc.prototype.segment = function(content, parent) {
      var seg;
      if (parent == null) {
        parent = null;
      }
      seg = {
        type: "div",
        cls: "segment",
        children: content
      };
      return _mapper.parseMapForParent(seg, parent);
    };

    Misc.prototype.columns = function(content, parent) {
      var col;
      if (parent == null) {
        parent = null;
      }
      col = {
        type: "div",
        cls: "columns",
        children: content
      };
      return _mapper.parseMapForParent(col, parent);
    };

    Misc.prototype.section = function(content, parent) {
      var sec;
      if (parent == null) {
        parent = null;
      }
      sec = {
        type: "div",
        cls: "section",
        children: content
      };
      return _mapper.parseMapForParent(sec, parent);
    };

    Misc.prototype.dynamicOption = function(name, desc, value, onValueChanged) {
      var body, header, row, trigger, triggerLink;
      header = _mapper.parseMapForParent({
        type: "span",
        cls: "text-mute tooltipped tooltipped-n",
        title: "" + name
      });
      header.setAttribute("aria-label", "" + desc);
      header = _mapper.parseMapForParent({
        type: "div",
        cls: "one-fifth column",
        children: header
      });
      triggerLink = _mapper.parseMapForParent({
        type: "a",
        href: "",
        title: "Change"
      });
      triggerLink.setAttribute("data-attr", "fast-editor-trigger");
      trigger = _mapper.parseMapForParent({
        type: "div",
        cls: "one-fifth column",
        children: triggerLink
      });
      body = _mapper.parseMapForParent({
        type: "div",
        cls: "three-fifths column",
        title: "" + value
      });
      body.setAttribute("data-attr", "fast-editor-texter");
      row = this.segment(this.columns([header, trigger, body]));
      row.setAttribute("data-attr", "fast-editor");
      new _FastEditor(row, function(status, value) {
        return typeof onValueChanged === "function" ? onValueChanged(status, value) : void 0;
      });
      return row;
    };

    Misc.prototype.staticOption = function(name, desc, content) {
      var body, header, trigger;
      header = _mapper.parseMapForParent({
        type: "span",
        cls: "text-mute tooltipped tooltipped-n",
        title: "" + name
      });
      header.setAttribute("aria-label", "" + desc);
      header = _mapper.parseMapForParent({
        type: "div",
        cls: "one-fifth column",
        children: header
      });
      trigger = _mapper.parseMapForParent({
        type: "div",
        cls: "one-fifth column",
        children: {
          type: "div",
          cls: "breadcrumb",
          title: ""
        }
      });
      body = _mapper.parseMapForParent({
        type: "div",
        cls: "three-fifths column",
        children: content
      });
      return this.segment(this.columns([header, trigger, body]));
    };

    Misc.prototype.staticTextOption = function(name, desc, value) {
      return this.staticOption(name, desc, {
        type: "span",
        title: "" + value
      });
    };

    return Misc;

  })();

  if (this.misc == null) {
    this.misc = new Misc;
  }

}).call(this);
