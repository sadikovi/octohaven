(function() {
  var Loader;

  Loader = (function() {
    function Loader() {}

    Loader.prototype.sendrequest = function(method, url, headers, payload, success, error) {
      var key, value, xmlhttp;
      xmlhttp = window.XMLHttpRequest ? new XMLHttpRequest : new ActiveXObject("Microsoft.XMLHTTP");
      xmlhttp.onreadystatechange = function() {
        var _ref;
        if (xmlhttp.readyState === 4) {
          if ((200 <= (_ref = xmlhttp.status) && _ref < 300)) {
            return typeof success === "function" ? success(xmlhttp.status, xmlhttp.responseText) : void 0;
          } else {
            return typeof error === "function" ? error(xmlhttp.status, xmlhttp.responseText) : void 0;
          }
        }
      };
      xmlhttp.open(method, url, true);
      for (key in headers) {
        value = headers[key];
        xmlhttp.setRequestHeader(key, value);
      }
      return xmlhttp.send(payload);
    };

    Loader.prototype.syncrequest = function(method, url, headers, payload) {
      var key, value, xmlhttp;
      xmlhttp = window.XMLHttpRequest ? new XMLHttpRequest : new ActiveXObject("Microsoft.XMLHTTP");
      xmlhttp.open(method, url, false);
      for (key in headers) {
        value = headers[key];
        xmlhttp.setRequestHeader(key, value);
      }
      return xmlhttp.send(payload);
    };

    return Loader;

  })();

  if (this.loader == null) {
    this.loader = new Loader;
  }

}).call(this);
