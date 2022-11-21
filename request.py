class Request:
    def __init__(self, method, target, version, headers, body=None):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.body = body

    def __str__(self):
        request = f"{self.method} {self.target} {self.version}"
        request += f"\n{self.headers}"[:-2]
        if self.body is not None:
            request += f"\n{self.body}"
        return request
