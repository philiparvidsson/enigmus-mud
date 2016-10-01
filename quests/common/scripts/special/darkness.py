# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus
import messages

from entities import Actor, Entity, Room

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
        light_class = enigmus.get_entity_class('special/light.py:Light')
        num_lights  = 0

        # Find all lights in room and inventories.

        inventories = [actor.inventory.entities for actor in self.room.entities
                           if isinstance(actor, Actor)]

        lights = [light for light in self.room.entities
                      if isinstance(light, light_class)]

        lights.extend([item for inventory in inventories for item in inventory
                           if isinstance(item, light_class)])

        for light in lights:
            if not light.is_on:
                continue

            num_lights += 1
            if num_lights >= self.lights_required:
                return False

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

    def replace_get_description(self, entity):
        entity.get_description_darkness = entity.get_description

        if isinstance(entity, Room):
            def get_description(exclude_actor=None):
                if self.is_dark():
                    if self.lights_required > 1:
                        return 'Ett väldigt mörkt rum.'
                    else:
                        return 'Ett mörkt rum.'

                return entity.get_description_darkness(exclude_actor)
        else:
            def get_description(indefinite=False):
                if self.is_dark():
                    return 'någon'

                return entity.get_description_darkness(indefinite)

        entity.get_description = get_description

    def restore_get_description(self, entity):
        if not hasattr(entity, 'get_description_darkness'):
            return

        entity.get_description = entity.get_description_darkness
        del entity.get_description_darkness

    def __container_add(self, container, entity):
        if entity == self:
            self.room = container
            self.replace_find_matches   (self.room)
            self.replace_get_description(self.room)
            return

        if isinstance(entity, Actor):
            self.replace_find_matches   (entity)
            self.replace_find_matches   (entity.inventory)
            self.replace_get_description(entity)

    def __container_remove(self, container, entity):
        if entity == self:
            self.restore_find_matches   (self.room)
            self.restore_get_description(self.room)
            return

        if isinstance(entity, Actor):
            self.restore_find_matches(entity)
            self.restore_find_matches(entity.inventory)
            self.restore_get_description(entity)
