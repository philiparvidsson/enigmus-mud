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
from entities.room          import BaseRoom

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
            'peka' : self.point,
            'pussa': self.kiss,
            'vinka': self.wave,
            'dansa': self.dance,
        }

    def kiss(self, player, args):
        matches = player.container.find_matches(' '.join(args))

        if len(matches) == 0 or (len(matches) == 1 and matches[0] == player):
            player.send('Pussa vem?')
            return

        for entity in matches:
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

        entity = player.container.find_best_match(' '.join(args))
        if not entity or entity == player:
            # Point at what?
            player.send('Peka på vad?')
            return

        # points at
        player.emote('pekar på', entity)

    def dance(self, player, args):
        if len(args) == 0:
            # dances
            player.emote('dansar en glad svängom med Herman, den osynlige kompisen')
            return

        if args[0] == 'med':
            args = args[1:]
            entity = player.container.find_best_match(' '.join(args))
            if not entity or entity == player:
                # Dance with what?
                player.send('Dansa med vem?')
                return

            player.emote('dansar livligt med', entity)

        def handle_tango(args):
            if len(args) == 0:
                player.emote('dansar en het tango')
                return

            if args[0] == 'med':
                args = args[1:]
                entity = player.container.find_best_match(' '.join(args))
                if not entity or entity == player:
                    # Dance with what?
                    player.send('Dansa med vem?')
                    return

                player.emote('dansar tango med', entity, 'så det svänger')

        def handle_kalinka(args):
            if len(args) == 0:
                player.emote('nynnar på Rysk folkmusik och dansar kalinka med framgång')
                return

            if args[0] == 'med':
                args = args[1:]
                entity = player.container.find_best_match(' '.join(args))
                if not entity or entity == player:
                    # Dance with what?
                    player.send('Dansa med vem?')
                    return

                player.emote('dansar kalinka framför', entity, 'som säkert undrar vad det ska vara bra för')

        def handle_bugg(args):
            if len(args) == 0:
                player.emote('tar en bugg själv på dansgolvet')
                return

            if args[0] == 'med':
                args = args[1:]
                entity = player.container.find_best_match(' '.join(args))
                if not entity or entity == player:
                    # Dance with what?
                    player.send('Dansa med vem?')
                    return

                player.emote('svänger lös med en uppfriskande bugg med', entity)

        dances = {'bugg', 'tango', 'kalinka'}
        if args[0] in dances:
            if   args[0] == 'bugg'   : handle_bugg(args[1:])
            elif args[0] == 'tango'  : handle_tango(args[1:])
            elif args[0] == 'kalinka': handle_kalinka(args[1:])

    def wave(self, player, args):
        if len(args) == 0:
            # waves
            player.emote('vinkar')
            return

        # to
        if args[0] == 'till':
            args = args[1:]

        entity = player.container.find_best_match(' '.join(args))
        if not entity or entity == player:
            # Wave to who?
            player.send('Vinka till vem?')
            return

        # waves to
        player.emote('vinkar till', entity)

    # ------- MESSAGES -------

    def __actor_emote(self, actor, args):
        room = actor.container

        if not room or not isinstance(room, BaseRoom):
            return

        for player in room.get_entities(Player):
            s = 'Du' if player == actor else actor.get_description()

            for arg in args:
                if isinstance(arg, basestring):
                    s += ' ' + arg
                else:
                    s += ' dig' if arg == actor else ' ' + arg.get_description(indefinite=False)

            player.send(lang.sentence(s))

    def __player_command(self, player, command):
        args    = command.split(' ')
        command = args[0]
        args    = args[1:]

        if command in self.emotes:
            self.emotes[command](player, args)
