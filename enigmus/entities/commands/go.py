# coding=utf-8

""" Provides the go command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core                   import messages
from entities.actor         import BaseActor
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

        self.on_message('room_enter', self.__room_enter,
            filter=messages.for_entities_of_class(Room))

        self.on_message('room_leave', self.__room_leave,
            filter=messages.for_entities_of_class(Room))

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

    def __room_enter(self, room, entity):
        actor = entity

        if not isinstance(actor, BaseActor):
            return

        for player in room.get_entities(Player):
            if player == actor:
                player.send(room.get_description())
            else:
                # {} arrived.
                player.send('{} kommer in.'.format(entity.get_description()))

    def __room_leave(self, room, entity):
        actor = entity

        if not isinstance(actor, BaseActor):
            return

        for player in room.get_entities(Player):
            s = entity.get_description(indeterminate=False)
            # {} left.
            player.send('{} gick.'.format(s))

