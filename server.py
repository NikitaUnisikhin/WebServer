import socket
import threading

clients = []
start_clients = []
stop = False


def main():
    """Запуск сервера"""
    host = socket.gethostname()
    port = 5000
    serv = socket.socket()
    serv.bind((host, port))
    serv.listen(100)
    global clients, start_clients

    def error_handling(e, client):
        if e.errno == 10053:
            clients.remove(client)
            start_clients.remove(client)
            print("Подключено пользователй:", len(clients))
        else:
            raise

    def send_messages(message):
        for client in clients:
            client.send(message.encode())

    def sender():
        """Отправляет команды клиентам"""
        global stop
        while not stop:
            global clients
            message = input(">>> ")
            if message == 'exit':
                stop = True
                serv.close()
                break
            send_messages(message)

    def acceptor():
        """Постоянно принимает новых клиентов"""
        global stop
        while not stop:
            global clients
            client, address = serv.accept()
            clients.append(client)
            print(f"Connection from: {address}")
            print("Подключено пользователй:", len(clients))

    def recv_data(client):
        while not stop:
            try:
                data = client.recv(1024)
                if data:
                    print(data.decode())
            except socket.error as e:
                error_handling(e, client)

    def indatas():
        while True:
            # Выполните цикл подключенных клиентов и создайте соответствующий поток
            for client in clients:
                # Если поток уже существует, пропустить
                if client in start_clients:
                    continue
                index = threading.Thread(target=recv_data, args=(client, ))
                index.start()
                start_clients.append(client)

    t1 = threading.Thread(target=acceptor)
    t1.start()

    t2 = threading.Thread(target=indatas)
    t2.start()

    t3 = threading.Thread(target=sender)
    t3.start()


if __name__ == '__main__':
    main()
