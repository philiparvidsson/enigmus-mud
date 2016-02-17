# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus
import messages

from entities import Item
from command  import Command

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

light_class = enigmus.instance.database.get_class('special/light.py:Light')
class Flashlight(Item, light_class):
    def __init__(self):
        super(Flashlight, self).__init__()

        self.describe('en' , ['svart' ], ['ficklampa' , 'lampa' ],
                      'den', ['svarta'], ['ficklampan', 'lampan'],
                      'En liten svart ficklampa. Den är av stilren modell och '
                      'får lätt plats i fickan tack vare sin storlek. Den ser '
                      'dyr ut.')
