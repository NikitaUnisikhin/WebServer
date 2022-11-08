class HTTPError(Exception):
    def __init__(self, status, reason, body=None):
        self.status = status
        self.reason = reason
        self.body = body