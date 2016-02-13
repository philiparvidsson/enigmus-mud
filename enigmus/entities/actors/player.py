# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus

from core                      import messages
from entities.actor import BaseActor
from entities.room       import Room

#-----------------------------------------------------------
# CONSTANTS
#-----------------------------------------------------------

MAX_BUFFER = 1024

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Player(BaseActor):
    def __init__(self, connection):
        super(Player, self).__init__()

        self._buffer = ''
        self._connection = connection

        self.state = LoggingInState(self)

        #self.on_message('room_enter'    , self.__on_room_enter,  filter=messages.for_nearby_entities(self))
        #self.on_message('room_leave'    , self.__on_room_leave,  filter=messages.for_nearby_entities(self))
        self.on_message('player_command', self.__on_player_command)

    def disconnect(self):
        self._connection.close()

    def receive(self, text):
        self._buffer += text.decode('iso-8859-1').encode('utf-8')

        if len(self._buffer) > MAX_BUFFER:
            self.disconnect()
            return

        i = self._buffer.find('\n')
        if i == -1:
            return None

        command = self._buffer[:i]
        self._buffer = self._buffer[i+1:]

        i = command.find('\r')
        if i >= 0:
            command = command[:i]

        self.state.perform(command)

    def send(self, text, end='\n'):
        text = text.replace('\r', '')

        s = ''

        while len(text) > 0:
            last_space = 0
            linebreak  = False
            counter    = 0

            for i in xrange(len(text)):
                if text[i] == ' ':
                    last_space = i
                elif text[i] == '\n':
                    counter = 0

                if counter >= 80:
                    if last_space == 0:
                        s   += text[:80] + '\n'
                        text = text[80:]
                    else:
                        s   += text[:last_space] + '\n'
                        text = text[last_space+1:]

                    linebreak = True
                    break

                counter += 1

            if not linebreak:
                s   += text
                text = ''

        s   = s  .replace('\n', '\r\n')
        end = end.replace('\n', '\r\n')

        self._connection.send(s  .decode('utf-8').encode('iso-8859-1'))
        self._connection.send(end.decode('utf-8').encode('iso-8859-1'))

    def __on_player_command(self, player, command):
        if player is not self:
            return False

        args = command.split(' ')

class State(object):
    def __init__(self, player):
        self.player = player

    def perform(self, command):
        pass

class LoggingInState(State):
    def __init__(self, player):
        super(LoggingInState, self).__init__(player)

        self.player.send('Välkommen till Enigmus!')
        self.player.send('Vad heter du? ', end='')

    def perform(self, command):
        if not hasattr(self.player, 'name'):
            self.player.name = command
            self.player.send('Hej, {}! Lösenord: '.format(command), end='')
        elif not hasattr(self.player, 'password'):
            self.player.password = command

            del self.player.password

            self.player.send('Tack! Ha så kul!')

            self.player.description = self.player.name
            self.player.state       = PlayingState(self.player)

            enigmus.instance.entities['Room_1'].add_entity(self.player)

class PlayingState(State):
    def __init__(self, player):
        super(PlayingState, self).__init__(player)

    def perform(self, command):
        self.player.post_message('player_command', self.player, command)
        self.player.send('Ok.')

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------

