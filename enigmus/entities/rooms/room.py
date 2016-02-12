# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core               import messagefilter
from entities.container import Container

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------


class Room(Container):
    def __init__(self):
        super(Room, self).__init__()

        self.description = '<Room is missing a description.>'
        self.exits       = {}

        self.on_message('container_add'   , self.__on_container_add)
        self.on_message('container_remove', self.__on_container_remove)
        self.on_message('player_command'  , self.__on_player_command, filter=messagefilter.in_container(self))

    def __on_container_add(self, container, entity):
        self.post_message('room_enter', self, entity)

    def __on_container_remove(self, container, entity):
        self.post_message('room_leave', self, entity)

    def __on_player_command(self, player, command):
        for exit in self.exits.keys():
            if command == exit:
                player.exit_room(exit)
                return True

        return False
