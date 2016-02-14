# coding=utf-8

""" Provides the actor base entity. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from entities.entity    import BaseEntity
from entities.item      import Item
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

    def drop(self, item, container=None):
        """ Drops the specified item from the actor's inventory into the
            specified container.

            :param item:      The item to drop.
            :param container: The container to drop the item into.

            :returns: True if the item was dropped successfully.
        """

        if not container and not self.container: return False
        if item.container != self.inventory    : return False

        if not container:
            container = self.container

        container.add_entity(item)
        self.post_message('actor_drop', self, container, item)

        return True

    def find_matches(self, text, keep_scores=False):
        matches = super(BaseActor, self).find_matches(text, keep_scores=True)

        matches.extend(self.inventory.find_matches(text, keep_scores=True))

        matches = sorted(matches, key=lambda x: x[0], reverse=True)
        if keep_scores:
            return matches

        return [x[1] for x in matches]

    def emote(self, verb, noun=None):
        self.post_message('actor_emote', self, verb, noun)

    def give(self, actor, item):
        """ Gives the specified item to the specified actor.

            :param actor: The actor to give an item to.
            :param item:  The item to give.

            :returns: True if the item was given successfully.
        """

        if item.container != self.inventory: return False

        self.inventory.remove_entity(item)
        actor.inventory.add_entity(item)
        self.post_message('actor_give', self, actor, item)

        return True

    def go(self, direction):
        """ Exits the room through the specified exit.

            :param direction: The exit to leave the room through.

            :returns: True if the room was exited successfully.
        """

        room = self.container

        #if not isinstance(room, Room): return False # TODO: Circular dependency.
        if direction not in room.exits: return False

        exit     = room.exits[direction]
        new_room = exit[0]

        room.remove_entity(self)
        self.post_message('actor_leave', self, room, exit[1])

        new_room.add_entity(self)
        self.post_message('actor_enter', self, new_room, exit[2])

        return True

    def match(self, text):
        """ Checks if the specified description matches the entity.

            :param description: The description to test against.

            :returns: True if the description matches the entity.
        """

        if text == 'alla':
            return 1

        return super(BaseActor, self).match(text)

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

        if not isinstance(item, Item)                     : return False
        if hasattr(item, 'takeable') and not item.takeable: return False

        container = item.container

        self.inventory.add_entity(item)
        self.post_message('actor_take', self, container, item)

        return True

    # ------- MESSAGES -------

    def __entity_cleanup(self):
        if not self.inventory:
            return

        for item in self.inventory.entities:
            self.drop(item)

        self.inventory.destroy()
        self.inventory = None

#-------------------------------------------------------------------------------

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
