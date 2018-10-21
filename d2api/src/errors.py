class BaseError(Exception):
    def __init__(self, msg):
        self._msg = msg
        
    def __str__(self):
        return repr(self._msg)

class APIAuthenticationError(BaseError):
    def __init__(self):
        self._msg = "HTTP 403: Authentication error. Invalid API Key."

class APITimeoutError(BaseError):
    def __init__(self):
        self._msg = "HTTP 503: Timeout error."