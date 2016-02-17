# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import messages

from entities import Entity
from command  import Command

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Light(Entity):
    def __init__(self):
        super(Light, self).__init__()

        self.is_on = False

class LightCommands(Command):
    def __init__(self):
        super(LightCommands, self).__init__()

        self.on_message('player_command', self.__player_command,
            filter=messages.for_actors_with_item_of_class(Light))

    def __player_command(self, player, command):
        args = command.split(' ')

        if args[0] == 'tänd':
            light = player.inventory.find_best_match(' '.join(args[1:]))
            if not isinstance(light, Light):
                player.text('Tänd vad?')
                return

            light.is_on = True
            player.emote('tände', light)
        elif args[0] == 'släck':
            light = player.inventory.find_best_match(' '.join(args[1:]))
            if not isinstance(light, Light):
                player.text('Släck vad?')
                return

            light.is_on = False
            player.emote('släckte', light)

LightCommands()
