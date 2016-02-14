# coding=utf-8

""" Provides the take command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core                   import lang
from core                   import messages
from entities.actors.player import Player
from entities.entity        import BaseEntity

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class InventoryCommand(BaseEntity):
    """ Command entity for handling the inventory command. """

    def __init__(self):
        """ Initializes the command. """

        super(InventoryCommand, self).__init__()

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
            player.send('Du har ingenting.')
            return

        inventory = player.inventory.entities
        items     = lang.list([x.get_description() for x in inventory])

        # You have: {}
        player.send('Du har: {}'.format(items))
