import asyncio
from http_error import HTTPError
from email.parser import Parser
from request import Request
from configuration import parsed_toml


MAX_LINE = 64 * 1024
MAX_HEADERS = 100
ENCODING = 'iso-8859-1'


# noinspection PyProtectedMember
class RequestParser:
    @staticmethod
    async def parse_request(conn):
        loop = asyncio.get_running_loop()
        is_first_row = True
        is_first_enter = True
        rows = []
        have_body = False
        ost = ''
        while True:
            data = str(await loop.sock_recv(conn, MAX_LINE), ENCODING)
            if '\n' not in data and is_first_row:
                raise HTTPError(400, 'Bad request',
                                'Request line is too long')
            elif '\n' not in data:
                raise HTTPError(494, 'Request header too large')

            split_data = data.split('\n')

            if is_first_row:
                rows += split_data[:-1]
                is_first_row = False
            else:
                rows.append(ost + split_data[0])
                rows += split_data[1:-1]
            ost = split_data[-1]

            if '' in rows and is_first_enter:
                is_first_enter = False
                for line in rows:
                    if 'Content-Length' in line:
                        have_body = True
                        break
                if have_body is False:
                    break

            if rows.count('') == 2 and have_body:
                break

        index_enter = rows.index('')
        method, target, ver = RequestParser.parse_request_line(rows[0])
        headers = RequestParser.parse_headers(rows[1:index_enter])

        body = None
        if have_body:
            body = RequestParser.parse_body(rows[index_enter+1:-1])

        host = headers.get('Host')
        if not host:
            raise HTTPError(400, 'Bad request',
                            'Host header is missing')

        if parsed_toml[host.split(".")[0]] is None:
            raise HTTPError(404, 'Not found')

        # if host not in (server._server_name,
        #                 f'{server._server_name}:{server._port}'):
        #     raise HTTPError(404, 'Not found')

        return Request(method, target, ver, headers, body)

    @staticmethod
    def parse_request_line(row):
        req_line = row
        words = req_line.split()

        if len(words) != 3:
            raise HTTPError(400, 'Bad request',
                            'Malformed request line')

        method, target, ver = words
        if ver != 'HTTP/1.1':
            raise HTTPError(505, 'HTTP Version Not Supported')
        return method, target, ver

    @staticmethod
    def parse_headers(headers):
        if len(headers) > MAX_HEADERS:
            raise HTTPError(494, 'Too many headers')

        shaders = '\n'.join(headers)
        return Parser().parsestr(shaders)

    @staticmethod
    def parse_body(rows):
        body = b""
        for row in rows:
            body += row.encode(ENCODING)
        return body
