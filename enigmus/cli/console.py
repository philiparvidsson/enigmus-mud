# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import importlib
import msvcrt
import pkgutil
import sys

#-----------------------------------------------------------
# GLOBALS
#-----------------------------------------------------------

interpreter = None
prompt      = '> '

_buffer = ''

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class CommandInterpreter(object):
    def __init__(self):
        self.commands = {}

    def interpret(self, command):
        args    = command.split(' ')
        command = args[0]
        args    = args[1:]

        if command not in self.commands:
            return False

        self.commands[command].perform(args)

    def register_command(self, name, command):
        if name in self.commands:
            print 'command already exists'
            return

        self.commands[name] = command

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------

def autocomplete():
    pass

def backspace():
    global _buffer

    if len(_buffer) == 0:
        return

    _buffer = _buffer[:-1]

def init():
    load_commands()

def load_commands():
    ci = CommandInterpreter()

    path = './enigmus/cli/commands/'
    for __, name, is_pkg in pkgutil.iter_modules([path]):
        module = importlib.import_module('cli.commands.%s' % name)
        ci.register_command(name, module.Command())

    global interpreter
    interpreter = ci

def update():
    global _buffer

    if not msvcrt.kbhit():
        return

    char = msvcrt.getch()

    if char == '\t':
        autocomplete()
    elif char == '\b':
        if len(_buffer) > 0:
            backspace()

            sys.stdout.write('\b \b')
            sys.stdout.flush()
    elif char == '\r':
        print

        global interpreter
        if interpreter:
            interpreter.interpret(_buffer)

        _buffer = ''

        global prompt
        print prompt,
    else:
        _buffer += char

        sys.stdout.write(char)
        sys.stdout.flush()
