from core import messages

room = 'Bosse'

def init():
    room.on_message('player_command', test_command, messages.all())

def test_command(player, command):
    if command != 'test':
        return

    player.text('Nu testar du bara va?')
