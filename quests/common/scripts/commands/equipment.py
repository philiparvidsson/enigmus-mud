# coding=utf-8

""" Provides the wear command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import messages

from command  import Command
from entities import Actor, Container, Detail, Entity, Player

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Commands(Command):
    """ Command entity for handling equipment commands. """

    def __init__(self):
        """ Initializes the command. """

        super(Commands, self).__init__()

        self.commands = {
            'ta av': self.remove,
            'ta på': self.wear
        }

        self.on_message('actor_remove', self.__actor_remove,
            filter=messages.for_entities_of_class(Actor))

        self.on_message('actor_wear', self.__actor_wear,
            filter=messages.for_entities_of_class(Actor))

    def remove(self, player, args):
        wearable = player.find_best_match(' '.join(args))

        if not wearable:
            player.text('Ta av dig vad?')
            return

        if not player.remove(wearable):
            # You're unable to remove {}.
            wearable_decs = wearable.get_description(indefinite=False)
            player.emote(player, 'försöker ta av', player, wearable,
                         'men misslyckas.')

    def wear(self, player, args):
        wearable = player.inventory.find_best_match(' '.join(args))

        if not wearable:
            player.text('Ta på dig vad?')
            return

        if not player.wear(wearable):
            player.emote(player, 'försöker ta på', player, wearable,
                         'men misslyckas.')

    # ------- MESSAGES -------

    def __actor_remove(self, actor, wearable):
        # removed
        actor.emote('tog av', actor, wearable)

    def __actor_wear(self, actor, wearable):
        # wears
        actor.emote('tog på', actor, wearable)
