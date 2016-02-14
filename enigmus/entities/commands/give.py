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

class GiveCommand(BaseEntity):
    """ Command entity for handling the give command. """

    def __init__(self):
        """ Initializes the command. """

        super(GiveCommand, self).__init__()

        self.on_message('actor_give', self.__actor_give,
            filter=messages.for_entities_of_class(Player))

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __actor_give(self, giver, receiver, item):
        # gave {} to
        giver.emote('gav {} till'.format(item.get_description()), receiver)

    def __player_command(self, player, command):
        args    = command.split(' ')
        command = args[0]
        args    = args[1:]

        # give
        if command != 'ge':
            return

        # to
        i = args.index('till') if 'till' in args else -1

        if i == -1:
            # Give what?
            player.send('Ge vad?')
            return

        item_desc  = ' '.join(args[:i]  )
        actor_desc = ' '.join(args[i+1:])

        item  = player.inventory.find_best_match(item_desc)
        actor = player.container.find_best_match(actor_desc)

        if not item:
            # Give what?
            player.send('Ge vad?')
            return

        item_desc = item.get_description(indefinite=False)

        if not actor or actor == player or not isinstance(actor, BaseActor):
            # Give {} to who?
            player.send('Ge {} till vem?'.format(item_desc))
            return

        player.give(actor, item)
