import socket
import os
import logging
from request import Request
from response import Response
from http_error import HTTPError
from email.parser import Parser
from configuration import parsed_toml
import asyncio
import aiofile


MAX_LINE = 64 * 1024
MAX_HEADERS = 100


class MyHTTPServer:
    def __init__(self, host, port, server_name):
        self._host = host
        self._port = port
        self._server_name = server_name
        self._users = {}

    async def serve(self):
        loop = asyncio.get_running_loop()
        serv_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            proto=0)

        try:
            serv_sock.bind((self._host, self._port))
            serv_sock.listen(parsed_toml["server"]["connection_max"])
            logging.info('Server start!')

            while True:
                conn, _ = await loop.sock_accept(serv_sock)
                logging.info('New connect!')
                try:
                    # loop.create_task(self.serve_client(conn))
                    await self.serve_client(conn)
                except Exception as e:
                    logging.warning(f"Client serving failed {e}")
        finally:
            serv_sock.close()
            logging.info("Close connect")

    async def serve_client(self, conn):
        try:
            req = await self.parse_request(conn)
            logging.info("\n" + str(req))
            resp = self.handle_request(req)
            self.send_response(conn, resp)
        except ConnectionResetError:
            conn = None
            logging.warning("Hard close connect!")
        except Exception as e:
            self.send_error(conn, e)

        if conn:
            conn.close()

    async def parse_request(self, conn):
        loop = asyncio.get_running_loop()
        is_first_row = True
        is_first_enter = True
        rows = []
        have_body = False
        ost = ''
        while True:
            data = str(await loop.sock_recv(conn, MAX_LINE), 'iso-8859-1')
            if '\n' not in data and is_first_row:
                raise HTTPError(400, 'Bad request',
                                'Request line is too long')
            elif '\n' not in data:
                raise HTTPError(494, 'Request header too large')

            split_data = data.split('\n')
            ost = split_data[-1]

            if is_first_row:
                rows += split_data[:-1]
                is_first_row = False
            else:
                rows.append(ost + split_data[0])
                rows += split_data[1:-1]
            ost = split_data[-1]

            if '' in rows and is_first_enter:
                for line in rows:
                    if 'Content-Length' in line:
                        have_body = True
                        break
                if have_body is False:
                    break

            if rows.count('') == 2 and have_body:
                break

        index_enter = rows.index('')
        method, target, ver = self.parse_request_line(rows[0])
        headers = self.parse_headers(rows[1:index_enter])

        body = None
        if have_body:
            body = self.parse_body(rows[index_enter+1:-1])

        host = headers.get('Host')
        if not host:
            raise HTTPError(400, 'Bad request',
                            'Host header is missing')
        if host not in (self._server_name,
                        f'{self._server_name}:{self._port}'):
            raise HTTPError(404, 'Not found')
        return Request(method, target, ver, headers, body)

    def parse_request_line(self, row):
        req_line = row
        words = req_line.split()
        if len(words) != 3:
            raise HTTPError(400, 'Bad request',
                            'Malformed request line')

        method, target, ver = words
        if ver != 'HTTP/1.1':
            raise HTTPError(505, 'HTTP Version Not Supported')
        return method, target, ver

    def parse_headers(self, headers):
        if len(headers) > MAX_HEADERS:
            raise HTTPError(494, 'Too many headers')

        sheaders = '\n'.join(headers)
        return Parser().parsestr(sheaders)

    def parse_body(self, rows):
        body = b""
        for row in rows:
            body += row.encode('iso-8859-1')
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
        raise HTTPError(404, "File not found")

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
        raise HTTPError(404, "File not found")

    def send_response(self, conn, resp):
        log_response = "\n"
        wfile = conn.makefile('wb')
        status_line = f'HTTP/1.1 {resp.status} {resp.reason}\r\n'
        log_response += status_line[:-1]
        wfile.write(status_line.encode('iso-8859-1'))

        if resp.headers:
            for (key, value) in resp.headers:
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


def main():
    # host = sys.argv[1]
    # port = int(sys.argv[2])
    # name = sys.argv[3]

    # host = "127.0.0.1"
    # port = 100
    # name = "server"

    host = parsed_toml["server"]["host"]
    port = parsed_toml["server"]["port"]
    name = parsed_toml["server"]["name"]

    serv = MyHTTPServer(host, port, name)
    logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w")
    try:
        asyncio.run(serv.serve())
        # serv.serve()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
