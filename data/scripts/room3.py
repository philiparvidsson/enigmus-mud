# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus

from core                   import messages
from entities.actors.player import Player
from entities.room          import BaseRoom

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Room3(BaseRoom):
    def __init__(self):
        super(Room3, self).__init__()

        self.on_message('player_command', self.enter_code,
            filter=messages.for_entities_in(self))

    def enter_code(self, player, command):
        args = command.split(' ')

        if args[0] != 'tryck':
            return

        if len(args) < 2 or args[1] != 'kod':
            player.send('Tryck vad? Kod?')
            return

        if len(args) < 3:
            player.send('Vilken kod vill du slå in?')
            return

        code = args[2]

        player.emote('slår in en kod.')

        player.text('*beep* *boop* *bip* piper terminalen när du trycker på '
                    'knapparna och slår in koden {}'.format(code))

        if code != '4973':
            player.text('Ingenting händer.')
            return

        room = player.container
        for p in room.get_entities(Player):
            p.text('Glasdörrarna till datasalen slår upp så snabbt att du hoppar '
                   'bakåt.')

        player.emote('går in i datasalen.')
        player.text('Glasdörrarna slår igen bakom dig.')

        enigmus.rooms['room7'].add_entity(player)
        player.text(player.container.get_description(exclude_actor=player))

        for p in room.get_entities(Player):
            p.text('Lika snabbt som de öppnas slår dörrarna igen, alldeles för '
                   'snabbt för att du skulle hinna gå in utan att vara beredd.')
