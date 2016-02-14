# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus

from core                      import messages
from entities.actor import BaseActor
from entities.room       import BaseRoom

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

        self.on_message('player_command', self.__on_player_command)
        self.on_message('player_text', self.__player_text)

    def disconnect(self):
        self._connection.close()

    def find_matches(self, text, keep_scores=False):
        matches = super(Player, self).find_matches(text, keep_scores=True)

        if self.container:
            matches.extend(self.container.find_matches(text, keep_scores=True))

        for item in self.inventory.entities:
            match = (item.match(text), item)
            if match[0] > 0:
                matches.append(match)

        matches = sorted(matches, key=lambda x: x[0], reverse=True)
        if keep_scores:
            return matches

        return [x[1] for x in matches]

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

    def send(self, text, end='\n', hard_breaks=True):
        text = text.replace('\r', '')
        s    = ''

        while len(text) > 0:
            last_space = 0
            linebreak  = False
            counter    = 0

            for i in xrange(len(text)):
                if text[i] == ' ':
                    last_space = i
                elif text[i] == '\n':
                    counter = 0

                if hard_breaks and counter >= 80:
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

    def text(self, text):
        self.post_message('player_text', text)

    def __on_player_command(self, player, command):
        if player is not self:
            return False

        args = command.split(' ')

    def __player_text(self, text):
        self.send(text)

class State(object):
    def __init__(self, player):
        self.player = player

    def perform(self, command):
        pass

class LoggingInState(State):
    def __init__(self, player):
        super(LoggingInState, self).__init__(player)

        self.player.send('''
   Välkommen till...
 ________            _
|_   __  |          (_)
  | |_ \_| _ .--.   __   .--./) _ .--..--.  __   _   .--.
  |  _| _ [ `.-. | [  | / /'`\;[ `.-. .-. |[  | | | ( (`\]
 _| |__/ | | | | |  | | \ \._// | | | | | | | \_/ |, `'.'.
|________|[___||__][___].',__` [___||__||__]'.__.'_/[\__) )
                       ( ( __))                    MUD       ''',
            hard_breaks=False)

        self.player.send('\nDet bästa spelet som någonsin gjorts!\n')
        self.player.send('Ange ditt namn: ', end='')

    def perform(self, command):
        if not hasattr(self.player, 'name'):
            self.player.name = command
            self.player.send('Hej {}! Ange lösenord: '.format(command), end='')
        elif not hasattr(self.player, 'password'):
            self.player.password = command

            del self.player.password

            self.player.send('Tack! Ha så kul!')

            self.player.description = self.player.name
            self.player.state       = PlayingState(self.player)

            enigmus.rooms['room1'].add_entity(self.player)
            self.player.send(self.player.container.get_description(exclude_actor=self.player))

class PlayingState(State):
    def __init__(self, player):
        super(PlayingState, self).__init__(player)

    def perform(self, command):
        self.player.post_message('player_command', self.player, command)

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------

