from response import Response


class HTTPError(Exception):
    def __init__(self, status, reason, body=None):
        self.status = status
        self.reason = reason
        self.body = body

    @staticmethod
    def send_error(conn, err):
        try:
            status = err.status
            reason = err.reason
            body = (err.body or err.reason).encode('iso-8859-1')
        except:
            status = 500
            reason = b'Internal Server Error'
            body = b'Internal Server Error'

        resp = Response(status, reason,
                        [('Content-Length', len(body))],
                        body.decode('iso-8859-1'))

        Response.send_response(conn, resp)
