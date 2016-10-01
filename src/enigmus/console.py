# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus
import msvcrt

#-----------------------------------------------------------
# GLOBALS
#-----------------------------------------------------------

commands = {}

interpreter = None
prompt      = '> '

_buffer = ''

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------

def exit(args):
    enigmus.exit()

#-------------------------------------------------------------------------------

def init():
    global commands
    commands = {
        'exit': exit,
        'quit': exit
    }

def update():
    if not msvcrt.kbhit():
        return

    command = raw_input('\n> ')

    global commands
    if not command in commands:
        print 'No such command:', command
        return

    args = command.split(' ')
    func = commands[args[0]](args[1:])

    print
