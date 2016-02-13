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
        if command != 't' and command != 'titta':
            return

        if len(args) == 1:
            player.send(player.container.get_description(exclude_actor=player))
            return

        args = args[1:]

        # at
        if len(args) > 1 and args[0] == 'på':
            args = args[1:]

        entity_of_interest = ' '.join(args)

        for entity in player.container.entities:
            if not entity.matches(entity_of_interest):
                continue

            # You see {}.
            player.send('Du ser {}.'.format(entity.get_description()))
            player.send(entity.long_description)
