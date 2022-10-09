import socket
import threading

# Создать клиентский объект
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Целевой хост
host = socket.gethostname()


while True:
    name = input('Пожалуйста, введите личный ник, не более десяти символов, менее одного символа')
    if 1 < len(name) < 10:
        break

# Порт назначения
port = 5000

# Подключить клиента
client.connect((host, port))
print('-' * 5 + 'подключился к серверу' + '-' * 5)
print('-' * 5 + 'Enter, чтобы закрыть соединение с сервером' + '-' * 5)


def outdatas():
    while True:
        # Введите информацию, которая будет отправлена на сервер
        outdata = input('')
        print()
        if outdata == 'enter':
            break
            # Отправить на сервер
        client.send(f'{name}:{outdata}'.encode('utf-8'))
        print('%s:%s' % (name, outdata))


def indatas():
    while True:
        # Принимаем информацию с сервера
        indata = client.recv(1024)
        # Закодировать полученную информацию
        print(indata.decode('utf-8'))


def main():
    # Создать многопоточность
    # Установить получение информации, объект потока
    t1 = threading.Thread(target=indatas)
    # Создание выходной информации, объект потока
    t2 = threading.Thread(target=outdatas)

    # Начать многопоточность
    t1.start()
    t2.start()


if __name__ == '__main__':
    main()

