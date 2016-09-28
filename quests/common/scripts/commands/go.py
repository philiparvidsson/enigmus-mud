# coding=utf-8

""" Provides the go command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import language
import messages

from entities import Actor, Entity, Player, Room

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Command(Entity):
    """ Command entity for handling the go command. """

    def __init__(self):
        """ Initializes the command. """

        super(Command, self).__init__()

        self.on_message('actor_enter', self.__actor_enter,
            filter=messages.for_entities_of_class(Actor))

        self.on_message('actor_leave', self.__actor_leave,
            filter=messages.for_entities_of_class(Actor))

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __actor_enter(self, actor, room, exit):
        actor_desc = actor.get_description()
        for player in room.get_entities(Player):
            if player == actor:
                player.text(room.get_description(exclude_actor=player))
            else:
                # {} comes in.
                player.text(language.sentence('{} kommer in.', actor_desc))

    def __actor_leave(self, actor, room, exit):
        actor_desc = actor.get_description(indefinite=False)
        for player in room.get_entities(Player):
            # {} left {}.
            player.text(language.sentence('{} gick {}.', actor_desc, exit))

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

        # north / down
        if direction == 'n':
            direction = 'norr' if 'norr' in room.exits else 'ner'

        if direction == 's': direction = 'söder'  # south
        if direction == 'u': direction = 'upp'    # up
        if direction == 'v': direction = 'väster' # west
        if direction == 'ö': direction = 'öster'  # east

        for exit in room.exits:
            if exit == direction:
                player.go(exit)
                return

        # go
        if args[0] == 'gå':
            # Go where?
            player.text('Gå vart?')
