(function() {
  var FastEditor, Panel;

  FastEditor = (function() {
    function FastEditor(_at_elem, _at_onDidFinishEdit, _at_oktext, _at_canceltext, _at_placeholder, _at_displayvalue) {
      var _ref;
      this.elem = _at_elem;
      this.onDidFinishEdit = _at_onDidFinishEdit;
      this.oktext = _at_oktext != null ? _at_oktext : "Save";
      this.canceltext = _at_canceltext != null ? _at_canceltext : "Cancel";
      this.placeholder = _at_placeholder != null ? _at_placeholder : "";
      this.displayvalue = _at_displayvalue != null ? _at_displayvalue : true;
      if (!(this.elem && this.elem.nodeType === Node.ELEMENT_NODE && this.hasDataAttribute(this.elem))) {
        throw new Error("Wrong element");
      }
      this.assets = {};
      _ref = [null, null], this.assets.texter = _ref[0], this.assets.trigger = _ref[1];
      this.discover(this.elem);
      if (!(this.assets.texter && this.assets.trigger)) {
        throw new Error("Insufficient structure");
      }
      FastEditor._util.addEventListener(this.assets.trigger, "click", (function(_this) {
        return function(e) {
          _this.showPanel();
          return e.preventDefault();
        };
      })(this));
      this.on = false;
    }

    FastEditor.prototype.getAttribute = function(elem) {
      return elem.getAttribute("data-attr");
    };

    FastEditor.prototype.hasDataAttribute = function(elem) {
      return this.getAttribute(elem) === "fast-editor";
    };

    FastEditor.prototype.hasTriggerAttribute = function(elem) {
      return this.getAttribute(elem) === "fast-editor-trigger";
    };

    FastEditor.prototype.hasTextAttribute = function(elem) {
      return this.getAttribute(elem) === "fast-editor-texter";
    };

    FastEditor.prototype.discover = function(node) {
      var elem, _i, _len, _ref, _results;
      if (!(node && node.childNodes)) {
        return false;
      }
      _ref = node.childNodes;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        elem = _ref[_i];
        if (elem && elem.nodeType === Node.ELEMENT_NODE) {
          if (this.hasTriggerAttribute(elem)) {
            _results.push(this.assets.trigger = elem);
          } else if (this.hasTextAttribute(elem)) {
            _results.push(this.assets.texter = elem);
          } else {
            _results.push(this.discover(elem));
          }
        } else {
          _results.push(void 0);
        }
      }
      return _results;
    };

    FastEditor.prototype.showPanel = function(value) {
      if (this.on) {
        return false;
      }
      value = value || ("" + this.assets.texter.textContent);
      this.panel = new Panel(value, this.placeholder, this.oktext, this.canceltext);
      this.assets.texter.innerHTML = "";
      this.assets.texter.appendChild(this.panel.html());
      this.assets.trigger.style.display = "none";
      FastEditor._util.addEventListener(this.panel.ok, "click", (function(_this) {
        return function(e) {
          var text;
          text = _this.panel.texter.value;
          if (typeof _this.hidePanel === "function") {
            _this.hidePanel(text);
          }
          if (typeof _this.onDidFinishEdit === "function") {
            _this.onDidFinishEdit(true, text);
          }
          return e.preventDefault();
        };
      })(this));
      FastEditor._util.addEventListener(this.panel.ko, "click", (function(_this) {
        return function(e) {
          if (typeof _this.hidePanel === "function") {
            _this.hidePanel();
          }
          if (typeof _this.onDidFinishEdit === "function") {
            _this.onDidFinishEdit(false);
          }
          return e.preventDefault();
        };
      })(this));
      return this.on = true;
    };

    FastEditor.prototype.hidePanel = function(value) {
      var _ref;
      if (!this.on) {
        return false;
      }
      this.assets.texter.textContent = (_ref = (this.displayvalue ? value : null)) != null ? _ref : this.panel.initvalue;
      this.panel = null;
      this.assets.trigger.style.display = "";
      return this.on = false;
    };

    return FastEditor;

  })();

  Panel = (function() {
    function Panel(_at_initvalue, _at_placeholder, _at_oktext, _at_canceltext) {
      var _ref;
      this.initvalue = _at_initvalue;
      this.placeholder = _at_placeholder != null ? _at_placeholder : "";
      this.oktext = _at_oktext != null ? _at_oktext : "Save";
      this.canceltext = _at_canceltext != null ? _at_canceltext : "Cancel";
      this.initvalue = this.initvalue ? this.initvalue.trim() : "";
      _ref = [this.submit(), this.cancel(), this.input(this.initvalue)], this.ok = _ref[0], this.ko = _ref[1], this.texter = _ref[2];
    }

    Panel.prototype.input = function(value) {
      var i, _ref;
      i = document.createElement("input");
      i.setAttribute("placeholder", "" + this.placeholder);
      _ref = ["text", "" + value], i.type = _ref[0], i.value = _ref[1];
      FastEditor._util.addClass(i, "form-control", "short");
      return i;
    };

    Panel.prototype.submit = function() {
      var s;
      s = document.createElement("div");
      s.innerHTML = "" + this.oktext;
      FastEditor._util.addClass(s, "btn", "btn-success");
      return s;
    };

    Panel.prototype.cancel = function() {
      var c;
      c = document.createElement("div");
      c.innerHTML = "" + this.canceltext;
      FastEditor._util.addClass(c, "btn");
      return c;
    };

    Panel.prototype.html = function() {
      var csec, isec, k, main, ssec, _divider, _i, _len, _ref;
      main = document.createElement("div");
      FastEditor._util.addClass(main, "breadcrumb");
      isec = document.createElement("div");
      FastEditor._util.addClass(isec, "section");
      isec.appendChild(this.texter);
      ssec = document.createElement("div");
      FastEditor._util.addClass(ssec, "section");
      ssec.appendChild(this.ok);
      csec = document.createElement("div");
      FastEditor._util.addClass(csec, "section");
      csec.appendChild(this.ko);
      _divider = function() {
        var divider;
        divider = document.createElement("div");
        FastEditor._util.addClass(divider, "separator");
        return divider;
      };
      _ref = [isec, _divider(), ssec, _divider(), csec];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        k = _ref[_i];
        main.appendChild(k);
      }
      return main;
    };

    return Panel;

  })();

  FastEditor._util = this.util;

  if (this.FastEditor == null) {
    this.FastEditor = FastEditor;
  }

}).call(this);
