# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core                   import messages
from entities.actors.player import Player

#-----------------------------------------------------------
# GLOBALS
#-----------------------------------------------------------

room = None

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------

def init():
    room.on_message('player_command', enter_code,
        filter=messages.for_entities_in(room))

def enter_code(player, command):
    args = command.split(' ')

    if args[0] != 'tryck':
        return

    if len(args) < 2 or args[1] != 'kod':
        player.send('Tryck vad? Kod?')
        return

    if len(args) < 3:
        player.send('Vilken kod vill du slå in?')
        return

    code = args[2]

    player.emote('slår in en kod.')

    player.text('*beep* *boop* *bip* piper terminalen när du trycker på '
                'knapparna och slår in koden {}'.format(code))

    if code != '4973':
        player.text('Ingenting händer.')
        return

    room = player.container
    for p in room.get_entities(Player):
        p.text('Glasdörrarna till datasalen slår upp så snabbt att du hoppar '
               'bakåt.')

    player.emote('går in i datasalen.')
    player.text('Glasdörrarna slår igen bakom dig.')

    #room7.add_entity(player)
    #player.text(room7.get_description(exclude_actor=player))

    for p in room.get_entities(Player):
        p.text('Lika snabbt som de öppnas slår dörrarna igen, alldeles för '
               'snabbt för att du skulle hinna gå in utan att vara beredd.')
