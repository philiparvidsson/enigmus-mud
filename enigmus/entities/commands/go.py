# coding=utf-8

""" Provides the go command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core                   import messages
from entities.actors.player import Player
from entities.entity        import BaseEntity
from entities.room          import Room

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class GoCommand(BaseEntity):
    """ Command entity for handling the go command. """

    def __init__(self):
        """ Initializes the command. """

        super(GoCommand, self).__init__()

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __player_command(self, player, command):
        if not player.container:
            return

        room = player.container
        if not isinstance(room, Room):
            return

        args      = command.split(' ')
        direction = args[0]

        # go
        if direction == 'gå' and len(args) > 0:
            direction = ' '.join(args[1:])
        else:
            direction = command

        for exit in room.exits:
            if exit == direction:
                player.go(exit)
                return

        # go
        if args[0] == 'gå':
            # Go where?
            player.send('Gå vart?')
