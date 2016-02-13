# coding=utf-8

""" Provides the take command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core                   import messages
from entities.actor         import BaseActor
from entities.actors.player import Player
from entities.entity        import BaseEntity
from entities.item          import BaseItem
from entities.room          import Room

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class DropCommand(BaseEntity):
    """ Command entity for handling the drop command. """

    def __init__(self):
        """ Initializes the command. """

        super(DropCommand, self).__init__()

        self.on_message('actor_drop', self.__actor_drop,
            filter=messages.for_entities_of_class(BaseActor))

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __actor_drop(self, actor, item):
        if not actor.container:
            return

        for entity in actor.container.get_entities(Player):
            if entity is not actor:
                # {} dropped {} on the ground.
                entity.send('{} slängde {} på marken.'.format(actor.get_description(indeterminate=False), item.get_description()))

    def __player_command(self, player, command):
        if not player.container:
            return

        args    = command.split(' ')
        command = args[0]

        # drop
        if command != 'släng':
            return

        item_to_drop = ' '.join(args[1:])

        for item in player.inventory.entities:
            if not item.matches(item_to_drop):
                continue

            player.drop(item)
            return

        # Drop what?
        player.send('Släng vadå?')

class InventoryCommand(BaseEntity):
    """ Command entity for handling the inventory command. """

    def __init__(self):
        """ Initializes the command. """

        super(InventoryCommand, self).__init__()

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __player_command(self, player, command):
        args    = command.split(' ')
        command = args[0]

        # drop
        if command != 'i' and command != 'inventarier':
            return

        if player.inventory.is_empty():
            # You're not carrying anything right now.
            player.send('Du bär inte på någonting just nu.')
            return

        items = ', '.join([x.get_description() for x in player.inventory.entities])

        # You're carrying: {}
        player.send('Du bär på: {}'.format(items))

class TakeCommand(BaseEntity):
    """ Command entity for handling the take command. """

    def __init__(self):
        """ Initializes the command. """

        super(TakeCommand, self).__init__()

        self.on_message('actor_take', self.__actor_take,
            filter=messages.for_entities_of_class(BaseActor))

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __actor_take(self, actor, item):
        if not actor.container:
            return

        for entity in actor.container.get_entities(Player):
            if entity is actor:
                # You took {}.
                entity.send('Du tog {}.'.format(item.get_description(indeterminate=False)))
            else:
                # {} took {}.
                entity.send('{} tog {}.'.format(actor.get_description(indeterminate=False), item.get_description(indeterminate=False)))

    def __player_command(self, player, command):
        if not player.container:
            return

        args    = command.split(' ')
        command = args[0]

        # take
        if command != 'ta':
            return

        item_to_take = ' '.join(args[1:])

        for entity in player.container.entities:
            if not entity.matches(item_to_take):
                continue

            if not player.take(entity):
                # You can't take that!
                player.send('Den kan du inte ta!')
                return

            # The item has been taken when this point is reached.
            return

        # Take what?
        player.send('Ta vad?')
