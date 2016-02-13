# coding=utf-8

""" Provides a room entity. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core               import messages
from entities.container import Container

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Room(Container):
    """ Represents a room with entities. """

    def __init__(self):
        """ Initializes the room. """

        super(Room, self).__init__()

        self.description = '<{} is missing a description.>'.format(self.id)
        self.exits       = {}

        self.on_message('container_add'   , self.__container_add   )
        self.on_message('container_remove', self.__container_remove)

    # ------- MESSAGES -------

    def __container_add(self, container, entity):
        self.post_message('room_enter', self, entity)

    def __container_remove(self, container, entity):
        self.post_message('room_leave', self, entity)
