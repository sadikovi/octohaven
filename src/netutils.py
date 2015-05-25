#!/usr/bin/env python

from types import IntType

# success
code_success, status_success = 200, "success"
# warning
code_warning, status_warning = 211, "warning"
# error
status_error = "error"
code_error400 = 400
code_error401 = 401
code_error500 = 500

class APIResultStatus(object):
    def __init__(self, code, status):
        self._code = code
        self._status = str(status)

# success status
class APIResultStatusSuccess(APIResultStatus):
    def __init__(self):
        super(APIResultStatusSuccess, self).__init__(code_success, status_success)

# warning status (code 211)
class APIResultStatusWarning(APIResultStatus):
    def __init__(self):
        super(APIResultStatusWarning, self).__init__(code_warning, status_warning)

# error statuses
## generic
class APIResultStatusError(APIResultStatus):
    def __init__(self, code):
        super(APIResultStatusError, self).__init__(code, status_error)
## code 400
class APIResultStatusError400(APIResultStatusError):
    def __init__(self):
        super(APIResultStatusError400, self).__init__(code_error400)
## code 401
class APIResultStatusError401(APIResultStatusError):
    def __init__(self):
        super(APIResultStatusError401, self).__init__(code_error401)
## code 500
class APIResultStatusError500(APIResultStatusError):
    def __init__(self):
        super(APIResultStatusError500, self).__init__(code_error500)

# result
class APIResult(object):
    def __init__(self, status, message):
        if not isinstance(status, APIResultStatus):
            raise TypeError("APIResultStatus expected, passed %s"%type(status))
        self._status = status
        self._message = str(message)

    def code(self):
        return self._status._code

    def status(self):
        return self._status._status

    def message(self):
        return self._message

    def dict(self):
        return {
            "code": self.code(),
            "status": self.status(),
            "messsage": self.message()
        }
