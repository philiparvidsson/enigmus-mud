# coding=utf-8

""" Provides the wear command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import messages

from entities import (Actor, Container, Detail, Entity, Player)

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Command(Entity):
    """ Command entity for handling the wear command. """

    def __init__(self):
        """ Initializes the command. """

        super(Command, self).__init__()

        self.on_message('actor_remove', self.__actor_remove,
            filter=messages.for_entities_of_class(Actor))

        self.on_message('actor_wear', self.__actor_wear,
            filter=messages.for_entities_of_class(Actor))

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __actor_remove(self, actor, wearable):
        # removed
        actor.emote('tog av', actor, wearable)

    def __actor_wear(self, actor, wearable):
        # wears
        actor.emote('tog på', actor, wearable)

    def __player_command(self, player, command):
        args    = command.split(' ')
        command = ' '.join(args[:2])
        args    = args[2:]

        if command == 'ta på':
            wearable = player.inventory.find_best_match(' '.join(args))

            if not wearable:
                player.text('Ta på dig vad?')
                return

            if not player.wear(wearable):
                player.emote(player, 'försöker ta på', player, wearable, 'men misslyckas.')

        elif command == 'ta av':
            wearable = player.find_best_match(' '.join(args))

            if not wearable:
                player.text('Ta av dig vad?')
                return

            if not player.remove(wearable):
                # You're unable to remove {}.
                player.text('Du lyckas inte ta av dig {}.'.format(wearable.get_description(indefinite=False)))
