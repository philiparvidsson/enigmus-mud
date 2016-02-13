# coding=utf-8

""" Provides a room entity. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core               import lang
from core               import messages
from entities.actor     import BaseActor
from entities.entity    import BaseEntity
from entities.container import Container
from entities.item      import Item

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

    def get_description(self, exclude_actor=None):
        """ Retrieves a description of the room.

            :returns: A description of the room, including its exits, any actors
                      in the room and any items in it.
        """

        room_desc  = lang.sentence(super(Room, self).get_description())
        exits_desc = lang.list(self.exits.keys())

        # {}\nExits: {}
        desc = '{}\nUtgångar: {}'.format(room_desc, exits_desc)

        actors = self.get_entities(BaseActor)
        if exclude_actor in actors:
            actors.remove(exclude_actor)
        if len(actors) > 0:
            # {} are here.
            desc += '\n' + lang.sentence('{} är här.', lang.list(actors))

        items = self.get_entities(Item)
        if len(items) > 0:
            desc += '\n' + lang.sentence('{}', lang.list(items))

        return desc
