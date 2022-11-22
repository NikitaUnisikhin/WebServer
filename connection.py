class Connection:
    def __init__(self, sock, connection_is_keep_alive=False):
        self.sock = sock
        self.connection_is_keep_alive = connection_is_keep_alive
