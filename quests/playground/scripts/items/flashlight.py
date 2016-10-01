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

class Flashlight(Item):
    def __init__(self):
        super(Flashlight, self).__init__()

        self.describe('en' , ['blå'], ['ficklampa' , 'lampa' ],
                      'den', ['blå'], ['ficklampan', 'lampan'],
                      'Den är gjord i plast och påminner om 80-talet. En'  \
                      'liten svart knapp sitter i mitten på den, vilket '  \
                      'möjligtvis kan vara startknappen som sätter igång ' \
                      'ficklampan. Längst ut har den en tjock, röd kant'   \
                      'runt lamphuset.')

        self.on_message('player_command', self._on_player_command, messages.for_nearby_entities(self))

    def _on_player_command(self, player, command):
        if command == 'tänd':
            self.description.add_indefinite_adjective('tänd', index=0)
            player.emote('tände {}'.format(self.get_description(indefinite=False)))
        elif command == 'släck':
            self.description.remove_indefinite_adjective('tänd')
            player.emote('släckte {}'.format(self.get_description(indefinite=False)))
