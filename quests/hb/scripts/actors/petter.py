# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus
import messages
import random

from entities import (Actor, Container, Player)

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Petter(Actor):
    def __init__(self):
        super(Petter, self).__init__()

        self.sex = 'male'

        self.describe('Petter',
                      'Petter är lång och smal med ett snällt ansikte. Han '
                      'ser väldigt tillfreds ut med tillvaron, men samtidigt '
                      'lite filosofisk och funderande. Hans hår är grått och '
                      'han har blå ögon')

        self.timer(self.wander, 10.0)

    def wander(self):
        self.go(random.choice(self.container.exits.keys()))
        self.timer(self.wander, random.uniform(15.0, 6.0))
