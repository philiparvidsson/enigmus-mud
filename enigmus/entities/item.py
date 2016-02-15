# coding=utf-8

""" Provides the base item class. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from entities.entity import BaseEntity

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Item(BaseEntity):
    """ Represents an item in the game. """

    def match(self, text):
        """ Checks if the specified description matches the entity.

            :param description: The description to test against.

            :returns: True if the description matches the entity.
        """

        if text == 'allt':
            return 1

        return super(Item, self).match(text)


class WearableItem(Item):
    """ Represents a wearable item in the game. """
    pass
