import socket
import sys
import os
from request import Request
from response import Response
from http_error import HTTPError
from email.parser import Parser

MAX_LINE = 64 * 1024
MAX_HEADERS = 100


class MyHTTPServer:
    def __init__(self, host, port, server_name):
        self._host = host
        self._port = port
        self._server_name = server_name
        self._users = {}

    def serve(self):
        serv_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            proto=0)

        try:
            serv_sock.bind((self._host, self._port))
            serv_sock.listen()
            print('Server start!')

            while True:
                conn, _ = serv_sock.accept()
                print('New connect!')
                try:
                    self.serve_client(conn)
                except Exception as e:
                    print('Client serving failed', e)
        finally:
            serv_sock.close()
            print("Close connect")

    def serve_client(self, conn):
        try:
            req = self.parse_request(conn)
            resp = self.handle_request(req)
            self.send_response(conn, resp)
        except ConnectionResetError:
            conn = None
            print("Hard close connect!")
        except Exception as e:
            self.send_error(conn, e)
            print("Error!")

        if conn:
            req.rfile.close()
            conn.close()

    def parse_request(self, conn):
        rfile = conn.makefile('rb')
        method, target, ver = self.parse_request_line(rfile)
        headers = self.parse_headers(rfile)
        body = None
        if headers.__getitem__('Content-Length') != None:
            body = self.parse_body(rfile)
        host = headers.get('Host')
        if not host:
            raise HTTPError(400, 'Bad request',
                            'Host header is missing')
        if host not in (self._server_name,
                        f'{self._server_name}:{self._port}'):
            raise HTTPError(404, 'Not found')
        return Request(method, target, ver, headers, rfile, body)

    def parse_request_line(self, rfile):
        raw = rfile.readline(MAX_LINE + 1)
        if len(raw) > MAX_LINE:
            raise HTTPError(400, 'Bad request',
                            'Request line is too long')

        req_line = str(raw, 'iso-8859-1')
        words = req_line.split()
        if len(words) != 3:
            raise HTTPError(400, 'Bad request',
                            'Malformed request line')

        method, target, ver = words
        if ver != 'HTTP/1.1':
            raise HTTPError(505, 'HTTP Version Not Supported')
        return method, target, ver

    def parse_headers(self, rfile):
        headers = []
        while True:
            line = rfile.readline(MAX_LINE + 1)
            if len(line) > MAX_LINE:
                raise HTTPError(494, 'Request header too large')

            if line in b'\r\n':
                break

            headers.append(line)
            if len(headers) > MAX_HEADERS:
                raise HTTPError(494, 'Too many headers')

        sheaders = b''.join(headers).decode('iso-8859-1')
        return Parser().parsestr(sheaders)

    def parse_body(self, rfile):
        body = b""
        while True:
            line = rfile.readline(MAX_LINE + 1)
            if len(line) > MAX_LINE:
                raise HTTPError(494, 'Request header too large')
            if line in (b'\r\n', b'\n', b''):
                break
            body += line

        return body

    def handle_request(self, req):
        if req.method == "GET":
            return self.handle_get_request(req)
        elif req.method == "POST":
            return self.handle_post_request(req)
        elif req.method == "HEAD":
            return self.handle_head_request(req)

    def handle_get_request(self, req):
        if os.path.isfile("C://Repos/WebServer/Server_Data/" + req.target):
            my_file = open("C://Repos/WebServer/Server_Data/" + req.target)
            data = my_file.read()
            my_file.close()
            return Response(200, "OK", None, data)

    def handle_post_request(self, req):
        if os.path.isfile("C://Repos/WebServer/Server_Data/" + req.target):
            raise HTTPError(495, "A file with the same name already exists on the server")
        else:
            my_file = open("C://Repos/WebServer/Server_Data/" + req.target, "w+")
        my_file.write(req.body.decode('iso-8859-1'))
        my_file.close()
        return Response(200, "OK")

    def handle_head_request(self, req):
        if os.path.isfile("C://Repos/WebServer/Server_Data/" + req.target):
            return Response(200, "OK")

    def send_response(self, conn, resp):
        wfile = conn.makefile('wb')
        status_line = f'HTTP/1.1 {resp.status} {resp.reason}\r\n'
        wfile.write(status_line.encode('iso-8859-1'))

        if resp.headers:
            for (key, value) in resp.headers:
                header_line = f'{key}: {value}\r\n'
                wfile.write(header_line.encode('iso-8859-1'))

        wfile.write(b'\r\n')

        if resp.body:
            wfile.write(resp.body.encode('iso-8859-1'))

        wfile.flush()
        wfile.close()

    def send_error(self, conn, err):
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
                        body)
        self.send_response(conn, resp)


if __name__ == '__main__':
    # host = sys.argv[1]
    # port = int(sys.argv[2])
    # name = sys.argv[3]

    host = "127.0.0.1"
    port = 100
    name = "server"

    serv = MyHTTPServer(host, port, name)
    try:
        serv.serve()
    except KeyboardInterrupt:
        pass
