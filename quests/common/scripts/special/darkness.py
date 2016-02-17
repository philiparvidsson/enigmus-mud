# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus
import messages
import random

from entities import Actor, Entity, Player, Room

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Darkness(Entity):
    def __init__(self):
        super(Darkness, self).__init__()

        self.lights_required = 1

        self.on_message('container_add', self.__container_add,
            filter=messages.for_container_of(self))

        self.on_message('container_remove', self.__container_remove,
            filter=messages.for_container_of(self))

    def is_dark(self):
        num_lights = 0
        for entity in self.room.entities:
            if isinstance(entity, Actor):
                for item in entity.inventory.entities:
                    if not isinstance(item, enigmus.instance.database.get_class('items/flashlight.py:Flashlight')):
                        continue

                    if item.is_on:
                        num_lights += 1
                        if num_lights >= self.lights_required:
                            return True

            if not isinstance(entity, enigmus.instance.database.get_class('items/flashlight.py:Flashlight')):
                continue

            if entity.is_on:
                num_lights += 1
                if num_lights >= self.lights_required:
                    return True

        return True

    def replace_find_matches(self, entity):
        entity.find_matches_darkness = entity.find_matches

        def find_matches(text, keep_scores=False):
            if self.is_dark():
                return []

            return entity.find_matches_darkness(text, keep_scores)

        entity.find_matches = find_matches

    def restore_find_matches(self, entity):
        if not hasattr(entity, 'find_matches_darkness'):
            return

        entity.find_matches = entity.find_matches_darkness
        del entity.find_matches_darkness

    def replace_get_description(self, room):
        room.get_description_darkness = room.get_description

        def get_description(exclude_actor=None):
            if self.is_dark():
                if self.lights_required > 1:
                    return 'Ett väldigt mörkt rum.'
                else:
                    return 'Ett mörkt rum.'

            return room.get_description_darkness(exclude_actor)

        room.get_description = get_description

    def restore_get_description(self, room):
        if not hasattr(room, 'get_description_darkness'):
            return

        room.get_description = room.get_description_darkness
        del room.get_description_darkness

    def __container_add(self, container, entity):
        if entity == self:
            self.room = container
            self.replace_find_matches(self.room)
            self.replace_get_description(self.room)
            return

        if isinstance(entity, Actor):
            self.replace_find_matches(entity)
            self.replace_find_matches(entity.inventory)

    def __container_remove(self, container, entity):
        if entity == self:
            self.restore_find_matches(self.room)
            self.restore_get_description(self.room)
            return

        if isinstance(entity, Actor):
            self.restore_find_matches(entity)
            self.restore_find_matches(entity.inventory)

