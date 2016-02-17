# coding=utf-8

""" Provides container related commands. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import language
import messages

from command import Command
from entities import (Actor, Container, Detail, Entity, Player)

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Commands(Command):
    """ Command entity for handling equipment commands. """

    def __init__(self):
        """ Initializes the command. """

        super(Commands, self).__init__()

        self.commands = {
            'stäng': self.close,
            't'    : self.look,
            'titta': self.look,
            'öppna': self.open
        }

        self.on_message('actor_close', self.__actor_close,
            filter=messages.for_entities_of_class(Actor))

        self.on_message('actor_open', self.__actor_open,
            filter=messages.for_entities_of_class(Actor))

    def close(self, player, args):
        if not player.container:
            return

        desc      = ' '.join(args)
        container = player.find_best_match(desc)

        if not container:
            container = player.container.find_best_match(desc)

        if not container or not isinstance(container, Container):
            # Close what?
            player.text('Stäng vad?')
            return

        if not container.is_open:
            # {} is already closed.
            player.text(language.sentence('{} är redan stängd.',
                        container.get_description(indefinite=False)))
            return

        if not player.close(container):
            player.emote('försöker stänga', container, 'men misslyckas')

    def look(self, player, args):
        if not player.container:
            return

        if len(args) == 0:
            player.text(player.container.get_description(exclude_actor=player))
            return

        look_inside = False

        # at
        if len(args) > 1 and args[0] == 'på':
            args = args[1:]
        # in
        elif len(args) > 1 and args[0] == 'i':
            args = args[1:]
            look_inside = True

        text   = ' '.join(args)
        entity = player.find_best_match(text)

        if not entity:
            entity = player.container.find_best_match(text)

        if look_inside:
            if not isinstance(entity, Container):
                entity = None
            elif not entity.is_open:
                # {} is closed!
                player.text(language.sentence('{} är stängd!', entity.get_description(indefinite=False)))
                return

        if not entity:
            # Look at/in what?
            player.text('Titta {} vad?'.format('i' if look_inside else 'på'))
            return

        if look_inside:
            if len(entity.entities) == 0:
                # {} is empty.
                player.text(language.sentence('{} är tom.', entity.get_description(indefinite=False)))
                return

            s = language.list([x.get_description() for x in entity.entities])
            # {} contains: {}
            player.text(language.sentence('{} innehåller: {}', entity.get_description(indefinite=False), s))
            return

        if not isinstance(entity, Detail):
            player.text(language.sentence(entity.get_description()))

        if isinstance(entity, Actor):
            player.text(entity.get_long_description(observer=player))
        else:
            player.text(entity.get_long_description())

    def open(self, player, args):
        if not player.container:
            return

        desc      = ' '.join(args)
        container = player.find_best_match(desc)

        if not container:
            container = player.container.find_best_match(desc)

        if not container or not isinstance(container, Container):
            # Open what?
            player.text('Öppna vad?')
            return

        if container.is_open:
            # {} is already open.
            player.text(language.sentence('{} är redan öppen.',
                        container.get_description(indefinite=False)))
            return

        if not player.open(container):
            player.emote('försöker öppna', container, 'men misslyckas')

    # ------- MESSAGES -------

    def __actor_close(self, actor, container):
        # closed
        actor.emote('stängde', container)

    def __actor_open(self, actor, wearable):
        # opened
        actor.emote('öppnade', wearable)
