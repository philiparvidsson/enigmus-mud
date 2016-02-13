# coding=utf-8

""" Provides the take command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core                   import lang
from core                   import messages
from entities.actor         import BaseActor
from entities.actors.player import Player
from entities.entity        import BaseEntity
from entities.item          import Item
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

    def __actor_drop(self, actor, container, item):
        if container != actor.container:
            # put {} in
            actor.emote('lade {} i'.format(item.get_description()), container)
        else:
            # put {} on the ground.
            actor.emote('lade {} på marken.'.format(item.get_description()))

    def __player_command(self, player, command):
        if not player.container:
            return

        args    = command.split(' ')
        command = args[0]
        args    = args[1:]

        # drop
        if command != 'släng':
            return

        container = None

        # in
        i = args.index('i') if 'i' in args else -1
        if i >= 0:
            container = player.container.find_match(' '.join(args[i+1:]))

            if not container:
                player.send('Släng i vad?')
                return

            args = args[:i]

        item = player.inventory.find_match(' '.join(args))

        if not item or item == container:
            # Drop what?
            player.send('Släng vadå?')
            return

        player.drop(item, container)

class GiveCommand(BaseEntity):
    """ Command entity for handling the give command. """

    def __init__(self):
        """ Initializes the command. """

        super(GiveCommand, self).__init__()

        self.on_message('actor_give', self.__actor_give,
            filter=messages.for_entities_of_class(Player))

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __actor_give(self, giver, receiver, item):
        # gave {} to
        giver.emote('gav {} till'.format(item.get_description()), receiver)

    def __player_command(self, player, command):
        args    = command.split(' ')
        command = args[0]
        args    = args[1:]

        # give
        if command != 'ge':
            return

        # to
        i = args.index('till') if 'till' in args else -1

        if i == -1:
            # Give what?
            player.send('Ge vad?')
            return

        item_desc  = ' '.join(args[:i]  )
        actor_desc = ' '.join(args[i+1:])

        item  = player.inventory.find_match(item_desc)
        actor = player.container.find_match(actor_desc)

        if not item:
            # Give what?
            player.send('Ge vad?')
            return

        item_desc = item.get_description(indefinite=False)

        if not actor or actor == player or not isinstance(actor, BaseActor):
            # Give {} to who?
            player.send('Ge {} till vem?'.format(item_desc))
            return

        player.give(actor, item)

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

        inventory = player.inventory.entities
        items     = lang.list([x.get_description() for x in inventory])

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

    def __actor_take(self, actor, container, item):
        if container != actor.container:
            # took {} from
            actor.emote('tog {} från'.format(item.get_description()), container)
        else:
            # took
            actor.emote('tog', item)

    def __player_command(self, player, command):
        if not player.container:
            return

        args    = command.split(' ')
        command = args[0]
        args    = args[1:]

        # take
        if command != 'ta':
            return

        container = player.container

        # from
        i = args.index('från') if 'från' in args else -1
        if i > 0:
            container = player.container.find_match(' '.join(args[i+1:]))

            if not container:
                # Take from what?
                player.send('Ta från vad?')
                return

            args = args[:i]

        item = container.find_match(' '.join(args))
        if not item:
            # Take what?
            player.send('Ta vad?')
            return

        if not player.take(item):
            # You can't take that!
            player.send('Den kan du inte ta!')
            return
