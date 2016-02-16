# coding=utf-8

""" Provides the open command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import language
import messages

from entities import (Actor, Container, Entity, Player)

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Command(Entity):
    """ Command entity for handling the open command. """

    def __init__(self):
        """ Initializes the command. """

        super(Command, self).__init__()

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __player_command(self, player, command):
        if not player.container:
            return

        args    = command.split(' ')
        command = args[0]
        args    = args[1:]

        # open
        if command != 'öppna':
            return

        s = ' '.join(args)
        container = player.find_best_match(s)

        if not container:
            container = player.container.find_best_match(s)

        if not container or not isinstance(container, Container):
            # Open what?
            player.text('Öppna vad?')
            return

        if container.is_open:
            # {} is already open.
            player.text(language.sentence('{} är redan öppen.', container.get_description(indefinite=False)))
            return

        container.open()
        # opened
        player.emote('öppnade', container)
