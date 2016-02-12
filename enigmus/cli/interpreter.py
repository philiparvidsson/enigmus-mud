# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

#-----------------------------------------------------------
# GLOBALS
#-----------------------------------------------------------

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
