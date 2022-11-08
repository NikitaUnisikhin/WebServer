class Request:
    def __init__(self, method, target, version, headers, rfile, body=None):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.rfile = rfile
        self.body = body

    # def body(self):
    #     size = self.headers.get('Content-Length')
    #     if not size:
    #         return None
    #     return self.rfile.read(size)
