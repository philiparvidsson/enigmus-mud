# coding=utf-8

""" Provides the take command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import language
import messages

from entities import (Entity, Player)

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Command(Entity):
    """ Command entity for handling the inventory command. """

    def __init__(self):
        """ Initializes the command. """

        super(Command, self).__init__()

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __player_command(self, player, command):
        args    = command.split(' ')
        command = args[0]

        # drop
        if command != 'i' and command != 'inventarier':
            return

        if player.inventory.is_empty():
            # You don't have anything.
            player.text('Du har ingenting.')
            return

        inventory = player.inventory.entities
        items     = language.list([x.get_description() for x in inventory])

        # You have: {}
        player.text('Du har: {}'.format(items))
