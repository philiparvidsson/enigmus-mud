# coding=utf-8

""" Provides the look command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core                   import lang
from core                   import messages
from entities.actors.player import Player
from entities.entity        import BaseEntity
from entities.room          import Detail

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class LookCommand(BaseEntity):
    """ Command entity for handling the look command. """

    def __init__(self):
        """ Initializes the command. """

        super(LookCommand, self).__init__()

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __player_command(self, player, command):
        if not player.container:
            return

        args    = command.split(' ')
        command = args[0]

        # look
        if command != 't' and command != 'titta':
            return

        if len(args) == 1:
            player.send(player.container.get_description(exclude_actor=player))
            return

        args = args[1:]

        # at
        if len(args) > 1 and args[0] == 'på':
            args = args[1:]

        text = ' '.join(args)

        entity_of_interest = player.container.find_match(text)

        if not entity_of_interest:
            entity_of_interest = player.inventory.find_match(text)

        if not entity_of_interest:
            # Look at what?
            player.send('Titta på vad?')
            return

        if not isinstance(entity_of_interest, Detail):
            player.send(lang.sentence(entity_of_interest.get_description()))
        player.send(entity_of_interest.long_description)
