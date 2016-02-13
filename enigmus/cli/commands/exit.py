# coding=utf-8

""" Provides the exit command. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Command(object):
    """ Provides the exit command for exiting the server. Always use this
        instead of pressing ctrl-c to ensure that the server is exited cleanly,
        that all data is saved etc.
    """

    usage = 'exit'

    def perform(self, args):
        """ Performs the exit command.

            :param args: Not used.
        """

        enigmus.exit()
