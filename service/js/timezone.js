(function() {
  var COOKIE_EXPIRE, COOKIE_NAME, c, d, jan, jul, timeoffset, _ref, _ref1, _ref2;

  if (navigator.cookieEnabled) {
    _ref = [999 * 24 * 60 * 60, "octohaven_timezone_cookie"], COOKIE_EXPIRE = _ref[0], COOKIE_NAME = _ref[1];
    _ref1 = [new Date, new Date], d = _ref1[0], c = _ref1[1];
    d.setTime(d.getTime() + (COOKIE_EXPIRE * 1000));
    _ref2 = [new Date(c.getFullYear(), 0, 1), new Date(c.getFullYear(), 6, 1)], jan = _ref2[0], jul = _ref2[1];
    timeoffset = Math.max(jan.getTimezoneOffset(), jul.getTimezoneOffset());
    document.cookie = COOKIE_NAME + "=" + timeoffset + ";expires=" + (d.toUTCString()) + ";Path=/;";
  } else {
    console.log("Cannot save timezone, cookies are disabled");
  }

}).call(this);
