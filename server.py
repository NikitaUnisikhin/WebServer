import socket
import os
import logging
from response import Response
from http_error import HTTPError
from configuration import parsed_toml
from database import get_path_to_data
from request_parser import RequestParser
from connection import Connection
import asyncio


MAX_CONNECTIONS = parsed_toml["server"]["connection_max"]


class MyHTTPServer:
    def __init__(self, host, port, server_name):
        self._host = host
        self._port = port
        self._server_name = server_name
        self._users = {}

    async def serve(self):
        loop = asyncio.get_running_loop()
        server_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            proto=0)

        try:
            server_sock.bind((self._host, self._port))
            server_sock.listen(MAX_CONNECTIONS)
            logging.info('Server start!')

            while True:
                conn_sock, _ = await loop.sock_accept(server_sock)
                conn = Connection(conn_sock)
                logging.info('New connect!')
                try:
                    await self.handle_connect(conn)
                except Exception as e:
                    logging.warning(f"Client serving failed {e}")
        finally:
            server_sock.close()
            logging.info("Close connect")

    async def handle_connect(self, conn):
        while True:
            try:
                request = await RequestParser.parse_request(conn.sock, self)
                logging.info("\n" + str(request))
                response = self.handle_request(request, conn)
                Response.send_response(conn.sock, response)
            except ConnectionResetError:
                conn = None
                logging.warning("Hard close connect!")
            except Exception as e:
                HTTPError.send_error(conn, e)

            if not conn.connection_is_keep_alive:
                conn.sock.close()

    def handle_request(self, req, conn):
        if req.headers.get('Connection') == 'Keep-Alive':
            conn.connection_is_keep_alive = True
        else:
            conn.connection_is_keep_alive = False

        if req.method == "GET":
            return self.handle_get_request(req)
        elif req.method == "POST":
            return self.handle_post_request(req)
        elif req.method == "HEAD":
            return self.handle_head_request(req)

    def handle_get_request(self, req):
        if os.path.isfile(get_path_to_data(req.target)):
            my_file = open(get_path_to_data(req.target))
            data = my_file.read()
            my_file.close()
            return Response(200, "OK", None, data)
        raise HTTPError(404, "File not found")

    def handle_post_request(self, req):
        if os.path.isfile(get_path_to_data(req.target)):
            raise HTTPError(495, "A file with the same name already exists on the server")
        else:
            my_file = open(get_path_to_data(req.target), "w+")
        my_file.write(req.body.decode('iso-8859-1'))
        my_file.close()
        return Response(200, "OK")

    def handle_head_request(self, req):
        if os.path.isfile(get_path_to_data(req.target)):
            return Response(200, "OK")
        raise HTTPError(404, "File not found")


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
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
