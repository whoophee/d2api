#!/usr/bin/env python
# -*- coding: utf-8 -*-
class BaseError(Exception): # pragma: no cover
    """Generic error wrapper."""
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return repr(self._msg)

class APIAuthenticationError(BaseError):
    """Error for invalid API key."""
    def __init__(self, api_key = None):
        self._msg = "HTTP 403: Authentication error caused by API key \"{}\".".format(api_key)

class APIMethodUnavailable(BaseError):
    """Error if the API method is discontued/broken."""
    def __init__(self, method_url = None):
        self._msg = "HTTP 404: \"{}\" is an unsupported/discontinued API method.".format(method_url)

class APIInsufficientArguments(BaseError):
    """Error for incomplete API call."""
    def __init__(self, query = None, params = None):
        self._msg = "HTTP 400: Insufficient arguments for \"{0}\". Parameters provided: {1}".format(query, params)

class APITimeoutError(BaseError): # pragma: no cover
    """Error for server timeout."""
    def __init__(self):
        self._msg = "HTTP 503: Timeout error."