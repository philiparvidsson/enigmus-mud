# coding=utf-8

""" Provides the wear command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core                   import messages
from entities.actor         import BaseActor
from entities.actors.player import Player
from entities.container     import Container
from entities.entity        import BaseEntity
from entities.entity        import Detail

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class WearCommand(BaseEntity):
    """ Command entity for handling the wear command. """

    def __init__(self):
        """ Initializes the command. """

        super(WearCommand, self).__init__()

        self.on_message('actor_remove', self.__actor_remove,
            filter=messages.for_entities_of_class(BaseActor))

        self.on_message('actor_wear', self.__actor_wear,
            filter=messages.for_entities_of_class(BaseActor))

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __actor_remove(self, actor, wearable):
        # removed
        actor.emote('tog av sig', wearable)

    def __actor_wear(self, actor, wearable):
        # wears
        actor.emote('tog på', actor, wearable)

    def __player_command(self, player, command):
        args    = command.split(' ')
        command = ' '.join(args[:2])
        args    = args[2:]

        if command != 'ta på':
            return

        wearable = player.inventory.find_best_match(' '.join(args))

        if not wearable:
            player.text('Ta på dig vad?')
            return

        player.wear(wearable)
