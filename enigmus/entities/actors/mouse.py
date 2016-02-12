# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus

from core import messagefilter
from entities.baseentity import BaseEntity
from entities.actors.baseactor import BaseActor
from entities.actors.player import Player
from entities.items.baseitem import BaseItem
from entities.rooms.room import Room

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

        self.on_message('player_command', self._on_player_command, messagefilter.in_same_room(self))

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
        self.on_message('actor_speak', self._actor_speak, filter=messagefilter.in_same_room(self))
        self.on_message('room_enter', self._container_add, filter=messagefilter.in_same_room(self))
        self.on_message('room_leave', self._container_remove, filter=messagefilter.in_same_room(self))

    def talk(self):
        self.speak('Käft! Tilltala mig inte!')
        self.timer(self.talk, 22.0)

    def walk_around(self):
        self.exit_room(self.container.exits.keys()[0])
        self.timer(self.walk_around, 60.0)

        for p in self.mouse_room.get_entities(Player):
            p.send('Du guppar omkring i tarmen. Musen rör nog på sig.')

    def _actor_speak(self, actor, sentence):
        if actor is self:
            return

        if sentence.find('mus') == -1:
            return

        self.speak('Jamen skit i mig säger jag!!!!')
        self.exit_room(self.container.exits.keys()[0])

    def __on_entity_init(self):
        self.description = 'en grå mus'
        self.mouse_room = enigmus.create_room('En varm tarm. Du undrar vad som händer om du sparkar till den.')

        self.on_message('player_command', self._on_player_command, messagefilter.in_room(self.mouse_room))

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
