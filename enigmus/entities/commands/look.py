# coding=utf-8

""" Provides the look command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core                   import messages
from entities.actors.player import Player
from entities.entity        import BaseEntity

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class LookCommand(BaseEntity):
    """ Command entity for handling the look command. """

    def __init__(self):
        """ Initializes the command. """

        super(LookCommand, self).__init__()

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __player_command(self, player, command):
        if not player.container:
            return

        args    = command.split(' ')
        command = args[0]

        # look
        if (command == 't' or command == 'titta') and len(args) == 1:
            player.send(player.container.get_description())
            return

        # at
        if len(args) > 1 and args[1] == 'på':
            args = args[2:]

        entity_of_interest = ' '.join(args)

        for entity in player.container.entities:
            if not entity.matches(entity_of_interest):
                continue

            # You see {}
            player.send('Du ser {}'.format(entity.get_description()))
            #player.send(entity.long_description) not yet implemented
