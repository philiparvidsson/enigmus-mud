# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus

from core import messages
from entities.entity import BaseEntity
from entities.actor import BaseActor
from entities.actors.player import Player
from entities.item import BaseItem
from entities.room import Room

#-----------------------------------------------------------
# GLOBALS
#-----------------------------------------------------------

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Flashlight(BaseItem):
    def __init__(self):
        super(Flashlight, self).__init__()

        self.description = 'en blå ficklampa'

        self.on_message('player_command', self._on_player_command, messages.for_nearby_entities(self))

    def _on_player_command(self, player, command):
        if command == 'tänd':
            self.description = 'en lysande, blå ficklampa (den lyser som fan)'
            for p in player.container.get_entities(Player):
                p.send('{} tände en blå ficklampa.'.format(player.name))
            return True
        elif command == 'släck':
            self.description = 'en blå ficklampa'
            for p in player.container.get_entities(Player):
                p.send('{} släckte en blå ficklampa.'.format(player.name))
            return True
        return False

class Mouse(BaseActor):
    def __init__(self):
        super(Mouse, self).__init__()

        self.on_message('entity_init', self.__on_entity_init)
        self.on_message('actor_say', self._actor_speak, filter=messages.for_nearby_entities(self))
        self.on_message('room_enter', self._container_add, filter=messages.for_nearby_entities(self))
        self.on_message('room_leave', self._container_remove, filter=messages.for_nearby_entities(self))

    def talk(self):
        self.say('Käft! Tilltala mig inte!')
        self.timer(self.talk, 22.0)

    def walk_around(self):
        self.go(self.container.exits.keys()[0])
        self.timer(self.walk_around, 60.0)

        for p in self.mouse_room.get_entities(Player):
            p.send('Du guppar omkring i tarmen. Musen rör nog på sig.')

    def _actor_speak(self, actor, sentence):
        if actor is self:
            return

        if sentence.find('mus') == -1:
            return

        self.say('Jamen skit i mig säger jag!!!!')
        self.go(self.container.exits.keys()[0])

    def __on_entity_init(self):
        self.description = (('en' , ['liten', 'mysig'] , 'mus'  ),
                            ('den', ['lilla', 'mysiga'], 'musen'))

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
