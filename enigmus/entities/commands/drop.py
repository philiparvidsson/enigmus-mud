# coding=utf-8

""" Provides the drop command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core                   import messages
from entities.actor         import BaseActor
from entities.actors.player import Player
from entities.entity        import BaseEntity

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class DropCommand(BaseEntity):
    """ Command entity for handling the drop command. """

    def __init__(self):
        """ Initializes the command. """

        super(DropCommand, self).__init__()

        self.on_message('actor_drop', self.__actor_drop,
            filter=messages.for_entities_of_class(BaseActor))

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __actor_drop(self, actor, container, item):
        if container != actor.container:
            # put {} in
            actor.emote('la {} i'.format(item.get_description()), container)
        else:
            # put {} on the ground.
            actor.emote('la {} på marken.'.format(item.get_description()))

    def __player_command(self, player, command):
        if not player.container:
            return

        args    = command.split(' ')
        command = args[0]
        args    = args[1:]

        # drop / put
        if command != 'släng' and command != 'lägg':
            return

        container = None

        # in
        i = args.index('i') if 'i' in args else -1
        if i >= 0:
            container = player.container.find_match(' '.join(args[i+1:]))

            if not container:
                player.send('Släng i vad?')
                return

            args = args[:i]

        item = player.inventory.find_match(' '.join(args))

        if not item or item == container:
            # Drop what?
            player.send('Släng vadå?')
            return

        player.drop(item, container)
