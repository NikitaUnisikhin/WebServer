import socket


def main():
    with socket.create_connection(("127.0.0.1", 100)) as s:
        while True:
            request = input()
            s.sendall(request.encode("utf-8"))
            while True:
                data = s.recv(1024)
                if not data:
                    break
                print(data.decode("utf-8"))


if __name__ == '__main__':
    main()
