# coding=utf-8

""" Provides functions for logging. """

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------

def error(format, *args):
    """ Logs an error message.

        :param format: The message format string.
        :param args:   The message format arguments.
    """

    print 'error: ' + format.format(*args)

def info(format, *args):
    """ Logs an informational message.

        :param format: The message format string.
        :param args:   The message format arguments.
    """

    print format.format(*args)

def warn(format, *args):
    """ Logs a warning message.

        :param format: The message format string.
        :param args:   The message format arguments.
    """

    print 'warning: ' + format.format(*args)
