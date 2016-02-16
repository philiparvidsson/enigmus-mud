# coding=utf-8

""" Provides the close command handler. """

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
    """ Command entity for handling the close command. """

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

        # close
        if command != 'stäng':
            return

        s = ' '.join(args)
        container = player.find_best_match(s)

        if not container:
            container = player.container.find_best_match(s)

        if not container or not isinstance(container, Container):
            # Close what?
            player.text('Stäng vad?')
            return

        if not container.is_open:
            # {} is already closed.
            player.text(language.sentence('{} är redan stängd.', container.get_description(indefinite=False)))
            return

        container.close()
        # closed
        player.emote('stängde', container)
