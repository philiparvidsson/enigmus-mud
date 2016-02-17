# coding=utf-8

import enigmus

class Session(object):
    def __init__(self, player):
        self.player = player
        self.state  = LoggingInState(self)

class State(object):
    def __init__(self, session):
        self.session = session

    def handle_command(self, command):
        pass

class LoggingInState(State):
    def __init__(self, session):
        super(LoggingInState, self).__init__(session)

        self.session.player.send('''
   Välkommen till...
 ________            _
|_   __  |          (_)
  | |_ \_| _ .--.   __   .--./) _ .--..--.  __   _   .--.
  |  _| _ [ `.-. | [  | / /'`\;[ `.-. .-. |[  | | | ( (`\]
 _| |__/ | | | | |  | | \ \._// | | | | | | | \_/ |, `'.'.
|________|[___||__][___].',__` [___||__||__]'.__.'_/[\__) )
                       ( ( __))                    MUD       ''',
            hard_breaks=False)

        self.session.player.send('\nDet bästa spelet som någonsin gjorts!\n')
        self.session.player.send('Ange ditt namn: ', end='')

    def handle_command(self, command):
        if not hasattr(self.session.player, 'name'):
            self.session.player.name = command
            self.session.player.send('Hej {}! Ange lösenord: '.format(command), end='')
        elif not hasattr(self.session.player, 'password'):
            self.session.player.password = command

            del self.session.player.password

            self.session.player.send('Tack! Ha så kul!')

            self.session.player.description = self.session.player.name
            self.session.state = PlayingState(self.session)

            enigmus.instance.database.rooms['room1'].add_entity(self.session.player)
            self.session.player.send(self.session.player.container.get_description(exclude_actor=self.session.player))

class PlayingState(State):
    def __init__(self, session):
        super(PlayingState, self).__init__(session)

    def handle_command(self, command):
        self.session.player.post_message('player_command', self.session.player, command)
