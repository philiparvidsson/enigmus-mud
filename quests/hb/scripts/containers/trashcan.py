# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from entities import Container

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Trashcan(Container):
    def __init__(self):
        super(Trashcan, self).__init__()

        self.describe('en'  , ['svart' ], ['soptunna' , 'tunna' ],
                      'den' , ['svarta'], ['soptunnan', 'tunnan'],
                      'Soptunnan är rund och svart. Den är gjord av billig '
                      'glansig plast och verkar ganska ömtålig för att vara '
                      'soptunna. Trots det förefaller den fylla sin funktion '
                      'eftersom man åtminstone kan stoppa saker i den.')
