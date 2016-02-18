# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import language
import messages

from entities import Entity

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Light(Entity):
    def __init__(self):
        super(Light, self).__init__()

        self.is_on = False

    def switch_on(self):
        self.is_on = True

    def switch_off(self):
        self.is_on = False

class LightCommands(Entity):
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

            if light.is_on:
                light_desc = light.get_description(indefinite=False)
                player.text(language.sentence('{} är redan tänd.', light_desc))
                return

            light.switch_on()
            player.emote('tände', light)
        elif args[0] == 'släck':
            light = player.inventory.find_best_match(' '.join(args[1:]))
            if not isinstance(light, Light):
                player.text('Släck vad?')
                return

            if not light.is_on:
                light_desc = light.get_description(indefinite=False)
                player.text(language.sentence('{} är redan släckt.', light_desc))
                return

            light.switch_off()
            player.emote('släckte', light)

LightCommands()
