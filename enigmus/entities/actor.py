# coding=utf-8

""" Provides the actor base entity. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from entities.entity    import BaseEntity
from entities.item      import BaseItem
from entities.container import Container

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class BaseActor(BaseEntity):
    """ Represents an actor entity. """

    def __init__(self):
        """ Initializes the actor. """

        super(BaseActor, self).__init__()

        self.inventory = Inventory(10, self)

        self.on_message('entity_cleanup', self.__entity_cleanup)

    def drop(self, item):
        """ Drops the specified item from the actor's inventory.

            :param item: The item to drop.

            :returns: True if the item was dropped successfully.
        """

        if not self.container              : return False
        if item.container != self.inventory: return False

        self.container.add_entity(item)
        self.post_message('actor_drop', self, item)

        return True

    def emote(self, verb, noun=None):
        self.post_message('actor_emote', self, verb, noun)

    def go(self, exit):
        """ Exits the room through the specified exit.

            :param exit: The exit to leave the room through.

            :returns: True if the room was exited successfully.
        """

        room = self.container

        #if not isinstance(room, Room): return False # TODO: Circular dependency.
        if exit not in room.exits    : return False

        room.remove_entity(self)
        room.exits[exit].add_entity(self)

        return True

    def say(self, text):
        """ Says the specified text.

            :param text: The sentence to say.
        """

        self.post_message('actor_say', self, text)

    def take(self, item):
        """ Attempts to take the specified item.

            :param item: The item to take.

            :returns: True if the item was taken successfully.
        """
        if item.container != self.container:
            return False

        if not isinstance(item, BaseItem):
            return False

        self.inventory.add_entity(item)
        self.post_message('actor_take', self, item)

        return True

    # ------- MESSAGES -------

    def __entity_cleanup(self):
        if not self.inventory:
            return

        self.inventory.destroy()
        self.inventory = None

class Inventory(Container):
    """ Represents an actor inventory. """

    def __init__(self, owner, max_entities):
        """ Initializes the inventory.

            :param owner:        The inventory owner.
            :param max_entities: The max number of entities allowed.
        """

        super(Inventory, self).__init__()

        self.max_entities = max_entities
        self.owner        = owner

        self.on_message('entity_cleanup', self.__entity_cleanup)

    # ------- MESSAGES -------

    def __entity_cleanup(self):
        if not self.entities:
            return

        for item in self.entities:
            item.destroy()

        self.entities = None
