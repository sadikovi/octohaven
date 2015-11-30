(function() {
  var Mapper,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  Mapper = (function() {
    function Mapper() {
      this.parseMapForParent = __bind(this.parseMapForParent, this);
    }

    Mapper.prototype.createElement = function(type, parent) {
      var t;
      t = document.createElement(type);
      if (parent) {
        parent.appendChild(t);
      }
      return t;
    };

    Mapper.prototype.addEventListener = function(elem, event, handler) {
      if (elem.addEventListener) {
        return elem.addEventListener(event, handler, false);
      } else if (elem.attachEvent) {
        return elem.attachEvent('on' + event, handler);
      } else {
        return elem['on' + event] = handler;
      }
    };

    Mapper.prototype.parseMapForParent = function(map, parent) {
      var c, item, mprs, t, _i, _len;
      if (!map) {
        return false;
      }
      mprs = {
        type: 'type',
        cls: 'cls',
        id: 'id',
        title: 'title',
        href: 'href',
        target: 'target',
        src: 'src',
        inputvalue: 'inputvalue',
        inputtype: 'inputtype',
        placeholder: 'placeholder',
        optionselected: 'optionselected',
        children: 'children',
        text_last: 'text_last',
        onclick: 'onclick',
        onkeyup: 'onkeyup',
        arialabel: 'arialabel'
      };
      if ("nodeName" in map) {
        if (parent) {
          parent.appendChild(map);
        }
      } else if (mprs.type in map) {
        c = this.createElement(map[mprs.type], parent);
        if (mprs.id in map) {
          c.id = "" + map[mprs.id];
        }
        if (mprs.cls in map) {
          c.className = "" + map[mprs.cls];
        }
        if (mprs.href in map) {
          c.href = "" + map[mprs.href];
        }
        if (mprs.target in map) {
          c.target = "" + map[mprs.target];
        }
        if (mprs.src in map) {
          c.src = "" + map[mprs.src];
        }
        if (mprs.inputvalue in map) {
          c.value = "" + map[mprs.inputvalue];
        }
        if (mprs.inputtype in map) {
          c.type = "" + map[mprs.inputtype];
        }
        if (mprs.placeholder in map) {
          c.placeholder = "" + map[mprs.placeholder];
        }
        if (mprs.optionselected in map) {
          c.selected = map[mprs.optionselected];
        }
        if (mprs.arialabel in map) {
          c.setAttribute("aria-label", map[mprs.arialabel]);
        }
        if (mprs.onclick in map && map[mprs.onclick]) {
          this.addEventListener(c, 'click', function(e) {
            return map[mprs.onclick].call(this, e);
          });
        }
        if (mprs.onkeyup in map && map[mprs.onkeyup]) {
          this.addEventListener(c, 'keyup', function(e) {
            return map[mprs.onkeyup].call(this, e);
          });
        }
        if (mprs.title in map) {
          t = document.createTextNode("" + map[mprs.title]);
          if (mprs.children in map) {
            if (!(length in map)) {
              map[mprs.children] = [map[mprs.children]];
            }
            if (mprs.text_last in map && map[mprs.text_last]) {
              map[mprs.children].push(t);
            } else {
              map[mprs.children].unshift(t);
            }
          } else {
            map[mprs.children] = [t];
          }
        }
        if (mprs.children in map) {
          this.parseMapForParent(map[mprs.children], c);
        }
      } else {
        for (_i = 0, _len = map.length; _i < _len; _i++) {
          item = map[_i];
          this.parseMapForParent(item, parent);
        }
      }
      return c;
    };

    return Mapper;

  })();

  if (this.mapper == null) {
    this.mapper = new Mapper;
  }

}).call(this);
