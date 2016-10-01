# coding=utf-8

""" Provides the take command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import language
import messages

from entities import Entity, Player

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Command(Entity):
    def __init__(self):
        super(Command, self).__init__()

        self.commands = {}

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    def __player_command(self, player, command):
        if len(command) == 0:
            return

        s = command.split(' ')

        i = 1
        while i <= len(s):
            command = ' '.join(s[:i])
            args    = s[i:]

            if command in self.commands:
                self.commands[command](player, args)
                return

            i += 1
