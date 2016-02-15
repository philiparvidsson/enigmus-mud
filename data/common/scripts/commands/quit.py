# coding=utf-8

""" Provides the quit command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core                   import messages
from entities.actors.player import Player
from entities.entity        import BaseEntity

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Command(BaseEntity):
    """ Command entity for handling the say command. """

    def __init__(self):
        """ Initializes the command. """

        super(Command, self).__init__()

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __player_command(self, player, command):
        if command == 'quit':
            player.disconnect()
