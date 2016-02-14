# coding=utf-8

""" Provides the look command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core                   import lang
from core                   import messages
from entities.actors.player import Player
from entities.entity        import BaseEntity
from entities.entity        import Detail
from entities.container     import Container

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

        args        = command.split(' ')
        command     = args[0]

        # look
        if command != 't' and command != 'titta':
            return

        if len(args) == 1:
            player.send(player.container.get_description(exclude_actor=player))
            return

        args        = args[1:]
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

        if look_inside and not isinstance(entity, Container):
            entity = None

        if not entity:
            # Look at/in what?
            player.send('Titta {} vad?'.format('i' if look_inside else 'på'))
            return

        if look_inside:
            if len(entity.entities) == 0:
                # {} is empty.
                player.send(lang.sentence('{} är tom.', entity.get_description(indefinite=False)))
                return

            s = lang.list([x.get_description() for x in entity.entities])
            # {} contains: {}
            player.send(lang.sentence('{} innehåller: {}', entity.get_description(indefinite=False), s))
            return

        if not isinstance(entity, Detail):
            player.send(lang.sentence(entity.get_description()))
        player.send(entity.long_description)
