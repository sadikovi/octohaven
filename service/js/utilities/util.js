// Generated by CoffeeScript 1.9.0
(function() {
  var Util,
    __slice = [].slice,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  Util = (function() {
    function Util() {}

    Util.prototype.createElement = function(tagname, id, cls, text, parent) {
      var elem;
      if (!tagname) {
        return false;
      }
      elem = document.createElement(tagname);
      if (cls) {
        elem.className = cls;
      }
      if (id) {
        elem.id = id;
      }
      if (text) {
        elem.innerHTML = text;
      }
      if (parent) {
        parent.appendChild(elem);
      }
      return elem;
    };

    Util.prototype.clear = function(elem) {
      if (elem) {
        return elem.innerHTML = "";
      }
    };

    Util.prototype.addEventListener = function(elem, event, handler) {
      if (elem.addEventListener) {
        return elem.addEventListener(event, handler, false);
      } else if (elem.attachEvent) {
        return elem.attachEvent('on' + event, handler);
      } else {
        return elem['on' + event] = handler;
      }
    };

    Util.prototype.removeEventListener = function(elem, event, handler) {
      if (elem.removeEventListener) {
        return elem.removeEventListener(event, handler, false);
      } else if (elem.detachEvent) {
        return elem.detachEvent('on' + event, handler);
      } else {
        return elem['on' + event] = null;
      }
    };

    Util.prototype.addClass = function() {
      var c, classes, elem, m, x;
      elem = arguments[0], classes = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
      c = elem.className.trim();
      c = c ? c.split(' ') : [];
      m = c.concat((function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = classes.length; _i < _len; _i++) {
          x = classes[_i];
          if (x && __indexOf.call(c, x) < 0) {
            _results.push(x);
          }
        }
        return _results;
      })());
      return elem.className = m.join(' ');
    };

    Util.prototype.removeClass = function() {
      var c, classes, elem, x;
      elem = arguments[0], classes = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
      c = elem.className.split(' ');
      return elem.className = ((function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = c.length; _i < _len; _i++) {
          x = c[_i];
          if (__indexOf.call(classes, x) < 0) {
            _results.push(x);
          }
        }
        return _results;
      })()).join(' ');
    };

    Util.prototype.hasClass = function(elem, cls) {
      return __indexOf.call(elem.className.split(' '), cls) >= 0;
    };

    Util.prototype.quote = function(str) {
      return encodeURIComponent(str).replace(/[!'()*]/g, function(c) {
        return '%' + c.charCodeAt(0).toString(16);
      });
    };

    Util.prototype.isArray = function(obj) {
      return Array.isArray(obj) || {}.toString.call(obj) === '[object Array]';
    };

    Util.prototype.randomid = function() {
      return ("" + (Math.random())).split(".")[1];
    };

    Util.prototype.jsonOrElse = function(str, def) {
      var e, obj;
      if (def == null) {
        def = null;
      }
      try {
        obj = JSON.parse(str);
      } catch (_error) {
        e = _error;
        obj = def;
      }
      return obj;
    };

    return Util;

  })();

  if (this.util == null) {
    this.util = new Util;
  }

}).call(this);
