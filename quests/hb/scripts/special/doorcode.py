# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus
import messages
import random

from entities import (Entity, Player, Room)

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class DoorCode(Entity):
    def __init__(self):
        super(DoorCode, self).__init__()

        # Set from room file.
        self.code = ''
        self.room = ''

        self.describe('ett', [], ['kodlås'  , 'lås'  ],
                      ''   , [], ['kodlåset', 'låset'],
                      'Det är en liten kodterminal för att trycka in koder '
                      'med. Du förmodar att dörrarna till datasalen låses upp '
                      'om man trycker in rätt kod.')

        self.on_message('player_command', self.__player_command,
            filter=messages.for_nearby_entities(self))

    def __player_command(self, player, command):
        args = command.split(' ')

        if args[0] != 'tryck':
            return

        if len(args) < 2 or args[1] != 'kod':
            player.text('Tryck vad? Kod?')
            return

        if len(args) < 3:
            player.text('Vilken kod vill du trycka?')
            return

        code = args[2]

        player.emote('slår in en kod.')

        beeps = random.sample(['*beep*', '*bzzzt*', '*boop*', '*bip*', '*BEEP*'], min(4, len(code)))
        player.text('{} piper terminalen när du trycker på '
                    'knapparna och slår in koden {}'.format(' '.join(beeps), code))

        if code != self.code:
            player.text('Ingenting händer.')
            return

        room = player.container
        for p in room.get_entities(Player):
            p.text('Glasdörrarna till datasalen slår upp så snabbt att du hoppar '
                   'bakåt.')

        player.emote('går in i datasalen.')
        player.text('Glasdörrarna slår igen bakom dig.')

        enigmus.instance.database.rooms[self.room].add_entity(player)
        player.text(player.container.get_description(exclude_actor=player))
        for p in room.get_entities(Player):
            p.text('Lika snabbt som de öppnas slår dörrarna igen, alldeles för '
                   'snabbt för att du skulle hinna gå in utan att vara beredd.')
