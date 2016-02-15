# coding=utf-8

""" Provides the drop command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core                   import lang
from core                   import messages
from entities.actor         import BaseActor
from entities.actors.player import Player
from entities.container     import Container
from entities.entity        import BaseEntity

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Command(BaseEntity):
    """ Command entity for handling the drop command. """

    def __init__(self):
        """ Initializes the command. """

        super(Command, self).__init__()

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
            s = ' '.join(args[i+1:])
            container = player.find_best_match(s)

            if not container:
                container = player.container.find_best_match(s)

            if not container or not isinstance(container, Container):
                player.text('Släng i vad?')
                return

            if not container.is_open:
                # {} is closed!
                player.text(lang.sentence('{} är stängd!', container.get_description(indefinite=False)))
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
                player.text('Ta av dig {} först.'.format(item.get_description(indefinite=False)))
                continue

            if item != container:
                player.drop(item, container)
