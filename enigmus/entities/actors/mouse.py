# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus

from core import messages
from entities.entity import BaseEntity
from entities.actor import BaseActor
from entities.actors.player import Player
from entities.item import Item
from entities.room import BaseRoom

import random

#-----------------------------------------------------------
# GLOBALS
#-----------------------------------------------------------

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class MattPresent(Item):
    def __init__(self):
        super(MattPresent, self).__init__()

        self.opened = False

        self.describe('ett', ['mystiskt'], ['paket'  ],
                      'det', ['mystiska'], ['paketet'],
                      'Ett mystiskt paket. Det är inslaget i regnbågsfärgat ' \
                      'presentpapper. Det sitter en lapp på paketet.')

        self.detail('en lapp', 'Det står "Till Mattias" på lappen. Du undrar vad paketet innehåller. Du kanske skulle riva sönder det?')

        self.on_message('player_command', self._on_player_command, messages.for_nearby_entities(self))

    def _on_player_command(self, player, command):
        args = command.split(' ')

        if args[0] != 'riv':
            return

        if len(args) == 1 or args[1] != 'sönder':
            player.send('Riv sönder vad? Paketet?')
            return

        if len(args) == 2 or args[2] != 'paket':
            player.send('Riv sönder vad? Paketet?')
            return

        self.opened = True
        self.describe('ett', ['trasigt'], ['paket'  ],
                      'det', ['trasiga'], ['paketet'],
                      'Ett trasigt paket. Någon har redan rivit sönder och ' \
                      'öppnat det. Undra vad som fanns i det?')

        player.emote('river sönder presentpappret och öppnar det mystiska paketet.')

        def present_open():
            for player in present_open.player.container.get_entities(Player):
                player.send('En dildo hoppar ur paketet och flyger in i röven på {}.'.format(player.get_description(indefinite=False)))

            player.emote('skriker av smärta och njutning.')

            def haha(direction):
                haha.player.emote('börjar gå {} men stannar upp mitt i rörelsen eftersom det sitter en dildo fastkilad i röven.'.format(direction))
                return False

            haha.player = present_open.player

            present_open.player.go = haha

        present_open.player = player
        self.timer(present_open, 0.1)

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

class Mouse(BaseActor):
    def __init__(self):
        super(Mouse, self).__init__()

        self.on_message('entity_init', self.__on_entity_init)
        self.on_message('actor_say', self._actor_speak, filter=messages.for_nearby_entities(self))
        #self.on_message('room_enter', self._container_add, filter=messages.for_nearby_entities(self))
        #self.on_message('room_leave', self._container_remove, filter=messages.all())

    def talk(self):
        d = [
            'Käft! Tilltala mig inte!',
            'Säg. Inte. Ett. Jävla. Ord',
            'Hah, vilken ful jävel!',
            'Jag tror jag är förföljd!'
        ]
        self.say(random.choice(d))
        self.timer(self.talk, 22.0)

    def walk_around(self):
        e = self.container.exits.keys()[:]
        if 'mus' in e:
            e.remove('mus')

        self.go(random.choice(e))
        self.timer(self.walk_around, 60.0)

        for p in self.mouse_room.get_entities(Player):
            p.send('Du guppar omkring i tarmen. Musen rör nog på sig.')

    def _actor_speak(self, actor, sentence):
        if actor is self:
            return

        if sentence.find('mus') == -1:
            return

        d = [
            'Jamen skit i mig säger jag!!!!',
            'Alltså det var då själva FAAN!',
            'Nä nu jävlar får det vara NOG!!',
            'Det var det värsta!',
            'DRA DIT PEPPARN VÄXER!',
        ]
        self.say(random.choice(d))
        e = self.container.exits.keys()[:]
        if 'mus' in e:
            e.remove('mus')

        def walk(): self.go(random.choice(e))
        self.timer(walk, 0.1)

    def __on_entity_init(self):
        self.describe('en' , ['liten', 'mysig'] , ['mus'  ],
                      'den', ['lilla', 'mysiga'], ['musen'])

        self.long_description = 'Han ser fruktansvärt ilsken ut och darrar '  \
                                'nästan lite när han ser sig omkring. Hans '  \
                                'ögonbryn formar ett ilsket, svartmuskigt V ' \
                                'i pannan. Han ser fruktansvärt överviktig '  \
                                'ut för att vara en mus, och har ett gap så ' \
                                'stort att du får för dig att du skulle'      \
                                'kunna kliva in i det om du ville. Du får'    \
                                'en känsla av att han inte gillar din närvaro.'

        self.mouse_room = enigmus.create_room('En varm tarm. Du undrar vad som händer om du sparkar till den.')

        self.on_message('player_command', self._on_player_command, filter=messages.for_entities_in(self.mouse_room))

        self.timer(self.walk_around, 60.0)
        self.timer(self.talk, 22.0)

    def _container_add(self, container, entity):
        self.mouse_room.exits = { 'ut' : container }

        if not isinstance(container, Room):
            return

        container.exits['mus'] = self.mouse_room

    def _container_remove(self, container, entity):
        if not isinstance(container, Room):
            return

        if entity is not self:
            return

        del container.exits['mus']

    def _on_player_command(self, player, command):
        if command == 'sparka tarm':
            self.walk_around()

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------
