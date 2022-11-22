from response import Response
from connection import Connection


class HTTPError(Exception):
    def __init__(self, status, reason, body=None):
        self.status = status
        self.reason = reason
        self.body = body

    @staticmethod
    def send_error(conn: Connection, err):
        try:
            status = err.status
            reason = err.reason
            body = (err.body or err.reason + '\n').encode('iso-8859-1')
        except:
            status = 500
            reason = b'Internal Server Error'
            body = b'Internal Server Error'

        resp = Response(status, reason,
                        [('Content-Length', len(body))],
                        body.decode('iso-8859-1'))

        if conn.connection_is_keep_alive:
            resp.headers += [('Connection', 'Keep-Alive')]

        Response.send_response(conn.sock, resp)
