import logging


class Response:
    def __init__(self, status, reason, headers: dict = None, body=None):
        self.status = status
        self.reason = reason
        self.headers = headers
        self.body = body

    @staticmethod
    def send_response(conn, resp):
        log_response = "\n"
        wfile = conn.makefile('wb')
        status_line = f'HTTP/1.1 {resp.status} {resp.reason}\r\n'
        log_response += status_line[:-1]
        wfile.write(status_line.encode('iso-8859-1'))

        if resp.headers:
            for (key, value) in resp.headers.items():
                header_line = f'{key}: {value}\r\n'
                log_response += header_line
                wfile.write(header_line.encode('iso-8859-1'))

        wfile.write(b'\r\n')

        if resp.body:
            log_response += resp.body
            wfile.write(resp.body.encode('iso-8859-1'))

        logging.info(log_response)
        wfile.flush()
        wfile.close()
