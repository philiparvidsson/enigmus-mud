# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import select
import socket

#-----------------------------------------------------------
# CONSTANT
#-----------------------------------------------------------

BUF_SIZE = 1024

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class TcpConnection(object):
    """ Represents a connection to a TCP server. """

    def __init__(self, server, sock, addr):
        """ Initializes the connection with the specified parameters.

            :param server: The server that accepted the connection.
            :param sock:   The connection socket.
            :param addr:   The socket address.

        """

        self.address = addr
        self.server  = server

        self._socket = sock

    def close(self):
        """ Closes the connection and removes it from its server. """

        del self.server.connections[self._socket]

        self._socket.close()
        self._socket = None

        for func in self.server._disconnect_funcs:
            func(self)

    def is_open(self):
        """ Returns True if the connection is open. """

        return self._socket is not None

    def _receive(self):
        """ Receives data from the connection. """

        data = self._socket.recv(BUF_SIZE)

        if not data:
            self.close()
            return None

        for func in self.server._receive_funcs:
            func(self, data)

    def send(self, data):
        """ Sends data through the connection. """

        self._socket.send(data)

        for func in self.server._send_funcs:
            func(self, data)

#-------------------------------------------------------------------------------

class TcpServer(object):
    """ A TCP server that accepts incoming connections. """

    def __init__(self):
        """ Initializes the TCP server. """

        self.connections = {}

        self._connect_funcs    = []
        self._disconnect_funcs = []
        self._receive_funcs    = []
        self._send_funcs       = []
        self._socket           = None

    def disconnect_all(self):
        """ Disconnects all current connections from the server. """

        for conn in self.connections.values():
            conn.close()

    def listen(self, ip, port, backlog=10):
        """ Starts listening on the specified local endpoint.

            :param ip:      The IP to bind to.
            :param port:    The port to bind to.
            :param backlog: The size of the backlogging.
        """

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind((ip, port))
        sock.listen(backlog)

        self._socket = sock

    def on_connect(self, func):
        """ Adds the specified function as a callback for the connect event.

            :param func: The callback function.
        """

        self._connect_funcs.append(func)

    def on_disconnect(self, func):
        """ Adds the specified function as a callback for the disconnect event.

            :param func: The callback function.
        """

        self._disconnect_funcs.append(func)

    def on_receive(self, func):
        """ Adds the specified function as a callback for the receive event.

            :param func: The callback function.
        """

        self._receive_funcs.append(func)

    def on_send(self, func):
        """ Adds the specified function as a callback for the send event.

            :param func: The callback function.
        """

        self._send_funcs.append(func)

    def stop_listening(self):
        """ Stops listening for incoming connections. """

        if not self._socket:
            return

        self._socket.close()
        self._socket = None

    def update(self):
        """ Accepts incoming connections and receives data from them. """

        sockets = self.connections.keys()

        if self._socket is not None:
            sockets.append(self._socket)

        r, w, x = select.select(sockets, [], [], 0.0)

        for sock in r:
            if sock is self._socket:
                self._accept()
            else:
                self.connections[sock]._receive()

    def _accept(self):
        """ Accepts pending incoming connections. """

        sock, addr = self._socket.accept()
        conn       = TcpConnection(self, sock, addr)

        self.connections[sock] = conn

        for func in self._connect_funcs:
            func(conn)
