# coding=utf-8

""" Provides the take command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import language
import messages

from command  import Command
from entities import (Actor, Container, Detail, Entity, Player)

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Commands(Command):
    """ Command entity for handling inventory commands. """

    def __init__(self):
        """ Initializes the command. """

        super(Commands, self).__init__()

        self.commands = {
            'ge'         : self.give,

            'i'          : self.inventory,
            'inventarier': self.inventory,

            'lägg'       : self.drop,
            'släng'      : self.drop,

            'ta'         : self.take,
        }

        self.on_message('actor_drop', self.__actor_drop,
            filter=messages.for_entities_of_class(Actor))

        self.on_message('actor_give', self.__actor_give,
            filter=messages.for_entities_of_class(Actor))

        self.on_message('actor_take', self.__actor_take,
            filter=messages.for_entities_of_class(Actor))

    def drop(self, player, args):
        if not player.container:
            return

        container = None

        # in
        i = args.index('i') if 'i' in args else -1
        if i > 0:
            desc      = ' '.join(args[i+1:])
            container = player.find_best_match(desc)

            if not container:
                container = player.container.find_best_match(desc)

            if not container or not isinstance(container, Container):
                player.text('Släng i vad?')
                return

            if not container.is_open:
                # {} is closed!
                player.text(language.sentence('{} är stängd!',
                            container.get_description(indefinite=False)))
                return

            args = args[:i]

        items = player.find_matches(' '.join(args))

        if len(items) == 0 or (len(items) == 1 and items[0] == container):
            # Drop what?
            player.text('Släng vadå?')
            return

        for item in items:
            if item in player.wearables:
                # Remove {} first.
                item_desc = item.get_description(indefinite=False)
                player.text('Ta av dig {} först.'.format(item_desc))
                continue

            if item != container:
                player.drop(item, container)

    def give(self, player, args):
        # to
        i = args.index('till') if 'till' in args else -1

        if i == -1:
            # Give what?
            player.text('Ge vad?')
            return

        item_desc  = ' '.join(args[:i]  )
        actor_desc = ' '.join(args[i+1:])

        item  = player.inventory.find_best_match(item_desc )
        actor = player.container.find_best_match(actor_desc)

        if not item:
            # Give what?
            player.text('Ge vad?')
            return

        item_desc = item.get_description(indefinite=False)

        if not actor or actor == player or not isinstance(actor, Actor):
            # Give {} to who?
            player.text('Ge {} till vem?'.format(item_desc))
            return

        player.give(actor, item)

    def inventory(self, player, args):
        if player.inventory.is_empty():
            # You don't have anything.
            player.text('Du har ingenting.')
            return

        inventory = player.inventory.entities
        items     = language.list([x.get_description() for x in inventory])

        # You have: {}
        player.text('Du har: {}'.format(items))

    def take(self, player, args):
        if not player.container:
            return

        # To prevent conflict with wear/remove.
        if len(args) > 0 and (args[0] == 'på' or args[0] == 'av'):
            return

        container = player.container

        # from
        i = args.index('från') if 'från' in args else -1

        # in
        if i == -1:
            i = args.index('i') if 'i' in args else -1

        if i > 0:
            s = ' '.join(args[i+1:])
            container = player.find_best_match(s)

            if not container:
                container = player.container.find_best_match(s)

            if not container or not isinstance(container, Container):
                # Take from what?
                player.text('Ta från vad?')
                return

            if not container.is_open:
                # {} is closed!
                item_desc = container.get_description(indefinite=False)
                player.text(language.sentence('{} är stängd!', item_desc))
                return

            args = args[:i]

        items = container.find_matches(' '.join(args))

        if len(items) == 0:
            # Take what?
            player.text('Ta vad?')
            return

        for item in items:
            if isinstance(item, Detail):
                continue

            if not player.take(item):
                # tries to take {} but fails.
                item_desc = item.get_description(indefinite=False)
                player.emote('försöker ta {} men misslyckas.'.format(item_desc))

    # ------- MESSAGES -------

    def __actor_drop(self, actor, container, item):
        if container != actor.container:
            # put {} in
            actor.emote('la {} i'.format(item.get_description()), container)
        else:
            # put {} on the ground.
            actor.emote('la {} på marken.'.format(item.get_description()))

    def __actor_give(self, giver, receiver, item):
        # gave {} to
        giver.emote('gav {} till'.format(item.get_description()), receiver)

    def __actor_take(self, actor, container, item):
        if container != actor.container:
            # took {} from
            actor.emote('tog {} från'.format(item.get_description()), container)
        else:
            # took
            actor.emote('tog', item)
