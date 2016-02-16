# coding=utf-8

""" Provides the take command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import language
import messages

from entities import (Actor, Container, Detail, Entity, Player)

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Command(Entity):
    """ Command entity for handling the take command. """

    def __init__(self):
        """ Initializes the command. """

        super(Command, self).__init__()

        self.on_message('actor_take', self.__actor_take,
            filter=messages.for_entities_of_class(Actor))

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
                player.text(language.sentence('{} är stängd!', container.get_description(indefinite=False)))
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
