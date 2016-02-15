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

class ShoutCommand(BaseEntity):
    """ Command entity for handling the say command. """

    def __init__(self):
        """ Initializes the command. """

        super(ShoutCommand, self).__init__()

        self.on_message('actor_shout', self.__actor_shout,
            filter=messages.for_entities_of_class(BaseActor))

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __actor_shout(self, actor, sentence):
        # says "{}"
        actor.emote('skriker "{}"'.format(sentence.upper()))

    def __player_command(self, player, command):
        # shout
        if command.find('S') != 0 and command.find('skrik') != 0:
            return

        text = command

        i = text.find('S')
        if i == 0:
            # '
            text = text[1:]
        else:
            # skrik
            text = text[5:]

        text = text.strip()

        if len(text) == 0:
            # Shout what?
            player.text('Skrik vadå?')
            return

        player.shout(text)
