# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus

from entities.room import BaseRoom

import random

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Common(BaseRoom):
    def __init__(self):
        super(Common, self).__init__()

        self.timer(self.thunder, 30.0)

    def thunder(self):
        for player in enigmus.instance.players:
            if not player.container:
                continue

            s = random.choice([
                '*buller buller* Åska mullrar dovt i bakgrunden.',
                '*BANG BANNNNGG* Rummet blixtrar till och fönstrena skallrar av den höga smällen.'
            ])

            #player.text(self.s)

        #self.timer(self.thunder, random.uniform(20.0, 90.0))
