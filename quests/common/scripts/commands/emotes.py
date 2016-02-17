# coding=utf-8

""" Provides handlers for emote commands. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import language
import messages
import random

from command  import Command
from entities import (Actor, Entity, Player, Room)

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Commands(Command):
    """ Entity for handling emotes. """

    def __init__(self):
        """ Initializes the emote handler. """

        super(Commands, self).__init__()

        self.commands = {
            'peka'  : self.point,
            'pussa' : self.kiss,
            'vinka' : self.wave,
            'dansa' : self.dance,
            'smiska': self.spank
        }

        self.on_message('actor_emote', self.__actor_emote,
            filter=messages.for_entities_of_class(Actor))

    def spank(self, player, args):
        # check for modifier
        mod = 0
        if 'hårt' in args:
            args.remove('hårt')
            mod = 1

        matches = player.container.find_matches(' '.join(args))
        if len(matches) == 0 or (len(matches) == 1 and matches[0] == player):
            player.send('Smiska vem?')
            return

        for entity in matches:
            # spank
            if mod == 0:
                player.emote('smiskar', entity)
            else:
                s = random.choice([
                        '*SMACK*',
                        '*SMISK*',
                        '*SMASK*',
                        '*KAH-TISH*',
                    ])

                for agent in player.container.get_entities(Player):
                    agent.text(s)

                player.emote('smiskar', entity, 'hårt som fan! Det här måste handla om en fetish')

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
        # available dances
        dances = {'bugg', 'tango', 'kalinka'}

        # dance alone
        if len(args) == 0:
            # dances
            player.emote('dansar en glad svängom med Herman, den osynlige kompisen')
            return
        elif len(args) == 1 and args[0] in dances:
            if   args[0] == 'tango'  : dance = 'dansar en het tango'
            elif args[0] == 'kalinka': dance = 'nynnar på Rysk folkmusik och dansar kalinka'
            elif args[0] == 'bugg'   : dance = 'tar en bugg själv på dansgolvet'
            player.emote(dance)
            return

        # dance with someone / -thing
        if args[0] == 'med':
            args = args[1:]
            type_of_dance = 'none'
        elif args[0] in dances:
            type_of_dance = args[0]
            args = args[1:]
            if args[0] == 'med':
                args = args[1:]

        entity = player.container.find_best_match(' '.join(args))
        if not entity or entity == player:
            # Dance with what?
            player.send('Dansa med vem?')
            return

        if   type_of_dance == 'none'   : dance = ['dansar livligt med', entity]
        elif type_of_dance == 'tango'  : dance = ['dansar en het tango med', entity]
        elif type_of_dance == 'kalinka': dance = ['dansar kalinka framför', entity, 'som säkert undrar vad det ska vara bra för']
        elif type_of_dance == 'bugg'   : dance = ['dansar bugg med', entity, 'så det svänger']

        player.emote(*dance)

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

        if not room or not isinstance(room, Room):
            return

        #args = [actor] + list(args)
        for player in room.get_entities(Player):
            s = 'Du' if player == actor else actor.get_description()

            for arg in args:
                if isinstance(arg, basestring):
                    s += ' ' + arg
                    continue

                if player == actor:
                    s += ' sig' if arg == player else ' ' + arg.get_description(indefinite=False)
                else:
                    s += ' dig' if arg == player else ' ' + arg.get_description(indefinite=False)

            #s = language.pronouns(player, actor, *args)
            player.send(language.sentence(s))
