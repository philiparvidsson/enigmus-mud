# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import base64
import select
import sha
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

        return data

    def send(self, data):
        """ Sends data through the connection. """

        self._socket.send(data)

        for func in self.server._send_funcs:
            func(self, data)

#-------------------------------------------------------------------------------

class WebSocket(TcpConnection):
    def __init__(self, server, sock, addr):
        super(WebSocket, self).__init__(server, sock, addr)

        self._buffer = ''
        self._state = 0

        self._send_buf = ''

    def _receive(self):
        data = self._socket.recv(BUF_SIZE)

        if not data:
            self.close()
            return None

        if self._state == 0:
            self._buffer += data.replace('\r', '')

            if self._buffer.find('\n\n') > 0:
                lines = self._buffer.split('\n')
                headers = {}
                for line in lines:
                    if line.startswith('GET') or len(line) == 0:
                        continue

                    s = line.split(':')
                    name = s[0].strip()
                    value = s[1].strip()

                    headers[name] = value

                self._buffer = None
                self._send_handshake(headers)
                self._state = 1

                if len(self._send_buf) > 0:
                    self.send(self._send_buf)
        elif self._state == 1 and len(data) > 0:
            if not self._buffer:
                self._buffer = bytearray(memoryview(data).tobytes())
            else:
                self._buffer.append(memoryview(data).tobytes())

            self._recv_frame()

        return data

    def _recv_frame(self):
        b = self._buffer

        fin        = (b[0] >> 7) & 1
        rsv1       = (b[0] >> 6) & 1
        rsv2       = (b[0] >> 5) & 1
        rsv3       = (b[0] >> 4) & 1
        opcode     = (b[0] >> 5) & 0x0f
        mask       = (b[1] >> 7) & 1
        payloadlen = (b[1] >> 1) & 0x7f

        i = 2

        if payloadlen >= 126:
            assert False

        # all client->server messages are masked
        assert mask == 1

        key = b[i:i+4]
        i += 4

        data = b[i:i+payloadlen]

        for i in range(len(data)):
            data[i] = data[i] ^ key[i%4]

        #print 'recv', len(data), 'bytes:', data

        self._buffer = self._buffer[i+payloadlen:]

        for func in self.server._receive_funcs:
            func(self, data)

    def send(self, data):
        if self._state == 0:
            self._send_buf += data
        else:
            opcode = 1 # text frame
            while len(data) > 0:
                n = min(120, len(data))
                d = data[0:n]
                data = data[n:]

                s = bytearray()
                if len(data) == 0:
                    s.append(0x80 | opcode)
                else:
                    s.append(0x00 | opcode)

                s.append(len(d))
                s.extend(memoryview(d).tobytes())
                opcode = 0 # continuation frame

                super(WebSocket, self).send(s)

    def _send_handshake(self, headers):
        s = headers['Sec-WebSocket-Key'] + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        wsh = sha.new(s)
        ws_hash = base64.b64encode(wsh.digest())
        self._socket.send('HTTP/1.1 101 Switching Protocols\n')
        self._socket.send('Upgrade: websocket\n')
        self._socket.send('Connection: Upgrade\n')
        self._socket.send('Sec-WebSocket-Accept: {}\n'.format(ws_hash))
        self._socket.send('\n')

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
        conn       = WebSocket(self, sock, addr)

        self.connections[sock] = conn

        for func in self._connect_funcs:
            func(conn)
