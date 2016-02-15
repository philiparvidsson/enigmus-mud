# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from entities.item import Item

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class AlgorithmBook(Item):
    def __init__(self):
        super(AlgorithmBook, self).__init__()

        self.describe('en', ['tråkig'], ['bok om algoritmer'  , 'bok'  ],
                      ''  , [        ], ['boken om algoritmer', 'boken'],
                      'Det som imponerar mest med den här boken är hur tung '
                      'och tjock den är. Förutom att den även möjligtvis '
                      'innehåller världens tråkigaste och längsta text. Den '
                      'kan bara vara intressant för en riktig ärkenörd.')
