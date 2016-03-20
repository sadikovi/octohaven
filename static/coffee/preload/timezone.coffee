# Block of code to extract client's timezone
if navigator.cookieEnabled
  [COOKIE_EXPIRE, COOKIE_NAME] = [999*24*60*60, "octohaven_timezone_cookie"]
  [d, c] = [new Date, new Date]
  d.setTime(d.getTime() + (COOKIE_EXPIRE * 1000))
  [jan, jul] = [new Date(c.getFullYear(), 0, 1), new Date(c.getFullYear(), 6, 1)]
  timeoffset = Math.max jan.getTimezoneOffset(), jul.getTimezoneOffset()
  document.cookie = "#{COOKIE_NAME}=#{timeoffset};expires=#{d.toUTCString()};Path=/;"
else
  console.log "Cannot save timezone, cookies are disabled"
