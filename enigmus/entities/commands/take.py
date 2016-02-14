# coding=utf-8

""" Provides the take command handler. """

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

class TakeCommand(BaseEntity):
    """ Command entity for handling the take command. """

    def __init__(self):
        """ Initializes the command. """

        super(TakeCommand, self).__init__()

        self.on_message('actor_take', self.__actor_take,
            filter=messages.for_entities_of_class(BaseActor))

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __actor_take(self, actor, container, item):
        if container != actor.container:
            # took {} from
            actor.emote('tog {} från'.format(item.get_description()), container)
        else:
            # took
            actor.emote('tog', item)

    def __player_command(self, player, command):
        if not player.container:
            return

        args    = command.split(' ')
        command = args[0]
        args    = args[1:]

        # take
        if command != 'ta':
            return

        container = player.container

        # from
        i = args.index('från') if 'från' in args else -1

        # in
        if i == -1:
            i = args.index('i') if 'i' in args else -1

        if i > 0:
            container = player.container.find_match(' '.join(args[i+1:]))

            if not container:
                # Take from what?
                player.send('Ta från vad?')
                return

            args = args[:i]

        item = container.find_match(' '.join(args))
        if not item:
            # Take what?
            player.send('Ta vad?')
            return

        if not player.take(item):
            # You can't take that!
            player.send('Den kan du inte ta!')
            return
