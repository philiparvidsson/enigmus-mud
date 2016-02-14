# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus

from core import messages
from entities.actor import BaseActor
from entities.actors.player import Player
from entities.container import Container

import random

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Cissi(BaseActor):
    def __init__(self):
        super(Cissi, self).__init__()

        self.sex = 'female'

        self.describe('Cissi',
                      'Cissi är något mullig med gråbrunt, långt hår. Hon ser '
                      'snäll och trevlig ut, men något med hennes hållning '
                      'ger dig en stark känsla av pondus.')

        self.wearables.append(enigmus.create_entity('glasses.py:Glasses'))

        self.on_message('container_add', self.__container_add,
            filter=messages.for_nearby_entities(self))

    def push_player_out(self, player):
        if player.container != self.container:
            return

        self.emote('knuffar ut dig raskt från datasalen.')
        player.go('ut')

    def __container_add(self, container, entity):
        if not isinstance(entity, Player):
            return

        s = random.choice([
            'Nej-nej, här får du inte vara! Seså, ut med dig!',
            'Nähe du! Ge dig iväg!',
            'Nä, nu får du ge dig. Fuck off!'
        ])

        self.say(s)
        self.timer(self.push_player_out, 0.2, args=[entity])

