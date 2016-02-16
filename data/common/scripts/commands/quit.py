# coding=utf-8

""" Provides the quit command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import messages

from entities import (Entity, Player)

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Command(Entity):
    """ Command entity for handling the quit command. """

    def __init__(self):
        """ Initializes the command. """

        super(Command, self).__init__()

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __player_command(self, player, command):
        if command != 'quit':
            return

        player.disconnect()
