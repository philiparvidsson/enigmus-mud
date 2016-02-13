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

        self.on_message('actor_say'   , self.__on_actor_speak, filter=messages.for_nearby_entities(self))
        self.on_message('room_enter'    , self.__on_room_enter,  filter=messages.for_nearby_entities(self))
        self.on_message('room_leave'    , self.__on_room_leave,  filter=messages.for_nearby_entities(self))
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

    def send(self, text, end='\r\n'):
        self._connection.send(text.decode('utf-8').encode('iso-8859-1'))
        self._connection.send(end .decode('utf-8').encode('iso-8859-1'))

    def __on_actor_speak(self, actor, sentence):
        #if actor is self:
        #    self.send('Du säger "{}"'.format(sentence))
        #else:
        #    self.send('{} säger "{}"'.format(actor.description, sentence))
        pass

    def __on_room_enter(self, container, entity):
        if not isinstance(entity, BaseActor):
            return

        if entity is not self:
            self.send('{} kom.'.format(entity.description))
        elif isinstance(container, Room) and entity is self:
            room = container
            self.send(room.description)
            self.send('Utgångar: {}'.format(', '.join(room.exits.keys())))

            s = ', '.join([e.description for e in room.entities])
            self.send('Här finns {}'.format(s))

    def __on_room_leave(self, container, entity):
        if not isinstance(entity, BaseActor) or entity is self:
            return

        self.send('{} gick.'.format(entity.description))

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

