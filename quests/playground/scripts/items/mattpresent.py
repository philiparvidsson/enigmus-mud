# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus
import messages

from entities import *

import random

#-----------------------------------------------------------
# GLOBALS
#-----------------------------------------------------------

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class MattPresent(Item):
    def __init__(self):
        super(MattPresent, self).__init__()

        self.opened = False

        self.describe('ett', ['mystiskt'], ['paket'  ],
                      'det', ['mystiska'], ['paketet'],
                      'Ett mystiskt paket. Det är inslaget i regnbågsfärgat ' \
                      'presentpapper. Det sitter en lapp på paketet.')

        self.detail('en lapp', 'Det står "Till Mattias" på lappen. Du undrar vad paketet innehåller. Du kanske skulle riva sönder det?')

        self.on_message('player_command', self._on_player_command, messages.for_nearby_entities(self))

    def _on_player_command(self, player, command):
        args = command.split(' ')

        if args[0] != 'riv':
            return

        if len(args) == 1 or args[1] != 'sönder':
            player.send('Riv sönder vad? Paketet?')
            return

        if len(args) == 2 or args[2] != 'paket':
            player.send('Riv sönder vad? Paketet?')
            return

        self.opened = True
        self.describe('ett', ['trasigt'], ['paket'  ],
                      'det', ['trasiga'], ['paketet'],
                      'Ett trasigt paket. Någon har redan rivit sönder och ' \
                      'öppnat det. Undra vad som fanns i det?')

        player.emote('river sönder presentpappret och öppnar det mystiska paketet.')

        def present_open():
            for player in present_open.player.container.get_entities(Player):
                player.send('En dildo hoppar ur paketet och flyger in i röven på {}.'.format(player.get_description(indefinite=False)))

            player.emote('skriker av smärta och njutning.')

            def haha(direction):
                haha.player.emote('börjar gå {} men stannar upp mitt i rörelsen eftersom det sitter en dildo fastkilad i röven.'.format(direction))
                return False

            haha.player = present_open.player

            present_open.player.go = haha

        present_open.player = player
        Timer(present_open, 0.1)
