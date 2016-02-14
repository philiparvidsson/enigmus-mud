# coding=utf-8

""" Provides the say command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core                   import messages
from core                   import lang
from entities.actor         import BaseActor
from entities.actors.player import Player
from entities.entity        import BaseEntity

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class SayCommand(BaseEntity):
    """ Command entity for handling the say command. """

    def __init__(self):
        """ Initializes the command. """

        super(SayCommand, self).__init__()

        self.on_message('actor_say', self.__actor_say,
            filter=messages.for_entities_of_class(BaseActor))

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __actor_say(self, actor, sentence):
        # says "{}"
        actor.emote('säger "{}"'.format(sentence))

    def __player_command(self, player, command):
        # say
        if command.find('\'') != 0 and command.find('säg') != 0:
            return

        text = command

        i = text.find('\'')
        if i == 0:
            # '
            text = text[1:]
        else:
            # say
            text = text[5:]

        text = text.strip()

        if len(text) == 0:
            # Say what?
            player.send('Säg vadå?')
            return

        player.say(text)
