# coding=utf-8

""" Provides the echo command. """

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Command(object):
    """ Provides the echo command for echoing text back to the console. This is
        a dummy command.
    """

    usage = 'echo [text]'

    def perform(self, args):
        """ Performs the echo command.

            :param args: The text to echo back to the console.
        """

        text = ' '.join(args)

        print text
