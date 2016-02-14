# coding=utf-8

""" Provides handlers for emote commands. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core                   import lang
from core                   import messages
from entities.actor         import BaseActor
from entities.actors.player import Player
from entities.entity        import BaseEntity
from entities.room          import Room

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class EmoteHandler(BaseEntity):
    """ Entity for handling emotes. """

    def __init__(self):
        """ Initializes the emote handler. """

        super(EmoteHandler, self).__init__()

        self.on_message('actor_emote', self.__actor_emote,
            filter=messages.for_entities_of_class(BaseActor))

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(BaseActor))

        self.emotes = {
            'pussa': self.kiss,
            'peka' : self.point,
            'vinka': self.wave
        }

    def kiss(self, player, args):
        entity = player.container.find_match(' '.join(args))

        if not entity or entity == player:
            # Kiss who?
            player.send('Pussa vem?')
            return

        # kisses
        player.emote('pussar', entity)

    def point(self, player, args):
        if len(args) == 0:
            # points straight ahead
            player.emote('pekar rakt fram')
            return

        # at
        if args[0] == 'på':
            args = args[1:]

        entity = player.container.find_match(' '.join(args))
        if not entity or entity == player:
            # Point at what?
            player.send('Peka på vad?')
            return

        # points at
        player.emote('pekar på', entity)

    def wave(self, player, args):
        if len(args) == 0:
            # waves
            player.emote('vinkar')
            return

        # to
        if args[0] == 'till':
            args = args[1:]

        entity = player.container.find_match(' '.join(args))
        if not entity or entity == player:
            # Wave to who?
            player.send('Vinka till vem?')
            return

        # waves to
        player.emote('vinkar till', entity)

    # ------- MESSAGES -------

    def __actor_emote(self, actor, verb, noun):
        room = actor.container

        if not room or not isinstance(room, Room):
            return

        noun_desc = noun.get_description(indefinite=False) if noun else None
        format    = '{} {} {}'                             if noun else '{} {}'

        for player in room.get_entities(Player):
            is_actor = (player == actor)
            is_noun  = (player == noun )

            a = 'Du'  if is_actor else actor.get_description()
            b = 'dig' if is_noun  else noun_desc

            player.send(lang.sentence(format, a, verb, b))

    def __player_command(self, player, command):
        args    = command.split(' ')
        command = args[0]
        args    = args[1:]

        if command in self.emotes:
            self.emotes[command](player, args)
