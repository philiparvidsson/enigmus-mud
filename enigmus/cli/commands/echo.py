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

class Command(object):
    usage = 'echo [text]'

    def __init__(self):
        pass

    def perform(self, args):
        text = ' '.join(args)

        print text
