# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from entities import Container, WearableItem

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Glasses(WearableItem):
    def __init__(self):
        super(Glasses, self).__init__()

        self.describe('ett par', [], ['glasögon'  ],
                      ''       , [], ['glasögonen'],
                      'Glasögonen är av typisk modell. Bågarna är tunna och '
                      'linserna är tjocka. De ser ut att kunna vara trendiga '
                      'inom den akademiska världen.')
