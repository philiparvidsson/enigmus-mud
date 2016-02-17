# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus
import messages
import random

from entities import Actor, Container, Player, Timer

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Cissi(Actor):
    def __init__(self):
        super(Cissi, self).__init__()

        self.sex = 'female'

        self.describe('Cissi',
                      'Cissi är något mullig med gråbrunt, långt hår. Hon ser '
                      'snäll och trevlig ut, men något med hennes hållning '
                      'ger dig en stark känsla av pondus.')

        #self.wearables.append(enigmus.create_entity('glasses.py:Glasses'))

        self.on_message('actor_give', self.__actor_give,
            filter=messages.for_nearby_entities(self))

        self.on_message('container_add', self.__container_add,
            filter=messages.for_nearby_entities(self))

    def give_key(self, player):
        book = [x for x in self.inventory.entities if hasattr(x, 'cissi_wants_it')]
        key  = [x for x in self.inventory.entities if hasattr(x, 'quest_item')]

        if len(key) != 1 or len(book) != 1:
            return

        book = book[0]
        key  = key[0]

        self.say('Du! Gör mig en tjänst! Gå upp till mitt kontor och lägg boken i mitt skåp')
        self.give(player, book)
        self.give(player, key)

    def push_player_out(self, player):
        if player.container != self.container:
            return

        if any(hasattr(e, 'cissi_wants_it') for e in self.inventory.entities):
            return

        self.emote('knuffar ut dig raskt från datasalen.')
        player.go('ut')

    def read_book(self):
        has_book = len([x for x in self.inventory.entities if hasattr(x, 'cissi_wants_it')]) == 1
        if not has_book:
            return

        r = random.randint(0, 7)

        if   r == 0: self.emote('sätter fingret på en sida i boken och ser väldigt fundersam ut.')
        elif r == 1:
            for player in self.container.get_entities(Player):
                player.text('*frrrrrrrrrt!* låter det när Cissi bläddrar snabbt i boken.')
        elif r == 2: self.emote('nickar långsamt och läser i boken.')
        elif r == 3: self.emote('mumlar något ohörbart.')
        elif r == 4: self.emote('vippar tveksamt fram och tillbaka med huvudet.')
        elif r == 5: self.emote('gör en fundersam min.')
        elif r == 6: self.emote('sätter pekfingret mot glasögonen och skjuter dem intill näsan.')

        r = random.randint(0, 2)
        if r == 0:
            self.say(random.choice([
                'Hah, här står det ju om red-black trees!',
                'Nä-nä-nä, det här stämmer inte. Här står det fel!',
                'Nämen, Boyer-Moore! Var det inte den algoritmen Thires gillade så mycket?',
                'Just precis! Quickhull *är* linjär för slumpmässiga punktsamlingar!',
                'Det här måste vara den senaste utgåvan!',
                'Får jag behålla den här boken?',
                'Ja, jag säger då det. Det här blir min kvällslektyr framöver!',
                'Här kan man ju läsa om massa spännande algoritmer!'
            ]))

        Timer(self.read_book, random.uniform(7.0, 21.0))

    def __actor_give(self, giver, receiver, item):
        if receiver != self:
            return

        def give_back():
            self.give(giver, item)


        if not hasattr(item, 'cissi_wants_it'):
            self.say('Det där joxet vill jag inte ha!')
            Timer(give_back, 0.5)
            return

        def react():
            if not any(hasattr(e, 'quest_item') for e in self.inventory.entities):
                self.say('Lägg den i mitt skåp säger jag!')
                Timer(give_back, 0.5)
                return

            self.say('Hmmm..! Vad spännande!')
            self.emote('bläddrar i', item)
            Timer(self.read_book, random.uniform(3.0, 7.0))
            Timer(self.give_key, random.uniform(40.0, 50.0), args=[giver])

        Timer(react, 0.5)

    def __container_add(self, container, entity):
        if not isinstance(entity, Player):
            return

        if not any(hasattr(e, 'quest_item') for e in self.inventory.entities):
            return

        if any(hasattr(e, 'cissi_wants_it') for e in entity.inventory.entities):
            self.say('Vad har du där för något? Får jag se!?')
            Timer(self.push_player_out, 7.0, args=[entity])
            return

        s = random.choice([
            'Nej-nej, här får du inte vara! Seså, ut med dig!',
            'Nähe du! Ge dig iväg!',
            'Nä, nu får du ge dig. Fuck off!',
            'Här har du inget att göra! Iväg med dig!'
        ])

        self.say(s)
        Timer(self.push_player_out, 0.2, args=[entity])
