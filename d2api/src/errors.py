class BaseError(Exception):
    def __init__(self, msg):
        self._msg = msg
        
    def __str__(self):
        return repr(self._msg)

class APIAuthenticationError(BaseError):
    def __init__(self, api_key = None):
        self._msg = "HTTP 403: Authentication error caused by API key \"{}\".".format(api_key)

class APIMethodUnavailable(BaseError):
    def __init__(self, method_url = None):
        self._msg = "HTTP 404: \"{}\" is an unsupported/discontinued API method.".format(method_url)

class APIInsufficientArguments(BaseError):
    def __init__(self, query = None, params = {}):
        self._msg = "HTTP 400: Insufficient arguments for \"{}\". Parameters provided: {}".format(query, params)

class APITimeoutError(BaseError):
    def __init__(self):
        self._msg = "HTTP 503: Timeout error."