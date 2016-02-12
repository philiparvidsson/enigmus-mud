# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core.messaging import MessageQueue

import select
import socket

#-----------------------------------------------------------
# CONSTANT
#-----------------------------------------------------------

BUF_SIZE = 64

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class TcpConnection(object):
    ''' Represents a connection to a TCP server. '''

    def __init__(self, server, socket, address):
        ''' Initializes the connection with the specified parameters. '''

        self._socket = socket

        self.address = address
        self.server  = server

    def close(self):
        ''' Closes the connection and removes it from its server. '''

        del self.server.connections[self._socket]

        self._socket.close()
        self._socket = None

        self.server.post_message('disconnect', self)

    def is_open(self):
        ''' Returns True if the connection is open. '''

        return self._socket is not None

    def _receive(self):
        ''' Receives data from the connection. '''

        data = self._socket.recv(BUF_SIZE)

        if not data:
            self.close()
            return None

        self.server.post_message('receive', self, data)

    def send(self, data):
        ''' Sends data through the connection. '''
        self._socket.send(data)

        self.server.post_message('send', self, data)

class TcpServer(MessageQueue):
    ''' A TCP server that accepts incoming connections. '''

    def __init__(self):
        ''' Initializes the TCP server. '''

        super(TcpServer, self).__init__()

        self._socket = None

        self.connections = {}

    def disconnect_all(self):
        ''' Disconnects all current connections from the server. '''

        for socket, connection in self.connections.iteritems():
            connection.close()

    def listen(self, ip, port, backlog=10):
        ''' Starts listening on the specified local endpoint.

            :param ip:      The IP to bind to.
            :param port:    The port to bind to.
            :param backlog: The size of the backlog.
        '''

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((ip, port))
        s.listen(backlog)

        self._socket = s

    def stop_listening(self):
        ''' Stops listening for incoming connections. '''

        if self._socket is None:
            return

        self._socket.close()
        self._socket = None

    def update(self):
        ''' Accepts incoming connections and receives data from them. '''

        sockets = self.connections.keys()

        if self._socket is not None:
            sockets.append(self._socket)

        r, w, x = select.select(sockets, [], [], 0.0)

        for socket in r:
            if socket is self._socket:
                self._accept()
            else:
                self.connections[socket]._receive()

        self.process_pending_messages()

    def _accept(self):
        ''' Accepts pending incoming connections. '''

        socket, address = self._socket.accept()
        connection = TcpConnection(self, socket, address)

        self.connections[socket] = connection
        self.post_message('connect', connection)
