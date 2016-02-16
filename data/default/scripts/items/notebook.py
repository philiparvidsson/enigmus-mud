# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import messages

from entities import Item

import random

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Note(Item):
    def __init__(self, text):
        super(Note, self).__init__()

        adjs = self.random_adjectives()
        desc = 'Någon har skrivit en anteckning. Du läser: "{}"'.format(text)

        self.describe('en', adjs, ['anteckning'  , 'lapp'  , 'lappar'  ],
                      'en', adjs, ['anteckningen', 'lappen', 'lapparna'],
                      desc)

        #self.on_message('player_command', self.__player_command,
        #    filter=messages.for_actors_with_item(self))

    def random_adjectives(self):
        return random.choice([
            ['liten'    ],
            ['skrynklig'],
            ['trasig'   ],
            ['ihopvikt' ],
            ['avriven'  ],
            ['viktig'   ]
        ])

    def __player_command(self, player, command):
        args    = command.split(' ')
        command = args[0]
        args    = args[1:]

class Notebook(Item):
    def __init__(self):
        super(Notebook, self).__init__()

        self.describe('ett', ['svart' ], ['anteckningshäfte'  , 'häfte'],
                      'det', ['svarta'], ['anteckningshäftet', 'häftet'],
                      'Ett svart anteckningshäfte för den som vill anteckna '
                      'något.')

        self.on_message('player_command', self.__player_command,
            filter=messages.for_actors_with_item(self))

    def __player_command(self, player, command):
        args    = command.split(' ')
        command = args[0]
        args    = args[1:]

        if command != 'anteckna':
            return

        if len(player.inventory.get_entities(Pen)) == 0:
            player.text('Du har ingen penna!')

class Pen(Item):
    def __init__(self):
        super(Pen, self).__init__()

        self.describe('en', ['röd' ], ['penna' , 'pennor'  ],
                      'en', ['röda'], ['pennan', 'pennorna'],
                      'En röd penna för den som vill anteckna saker och ting.')

        self.on_message('player_command', self.__player_command,
            filter=messages.for_actors_with_item(self))

    def __player_command(self, player, command):
        args    = command.split(' ')
        command = args[0]
        args    = args[1:]

        if command != 'anteckna':
            return

        if len(player.inventory.get_entities(Notebook)) == 0:
            player.text('Du har inget anteckningsblock!')
            return

        note = Note(' '.join(args))

        player.emote('skriver en anteckning.')
        player.inventory.add_entity(note)
