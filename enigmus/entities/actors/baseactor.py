# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus

from entities.baseentity import BaseEntity
from entities.rooms.room import Room

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class BaseActor(BaseEntity):
    def __init__(self):
        super(BaseActor, self).__init__()

        self.inventory = []

    def destroy(self):
        super(BaseActor, self).destroy()

        if self.inventory:
            for item in self.inventory:
                item.destroy()

            self.inventory = None

    def exit_room(self, exit):
        room = self.container
        if not room:
            log.error('{} is not in a room', self)
            return

        if exit not in room.exits:
            log.error('room {} has no exit \'{}\'', self, exit)
            return

        room.remove_entity(self)
        room.exits[exit].add_entity(self)

    def speak(self, sentence):
        self.post_message('actor_speak', self, sentence)
