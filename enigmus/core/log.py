# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------

def error(format, *args):
    print 'error: ' + format.format(*args)

def info(format, *args):
    print format.format(*args)

def warn(format, *args):
    print 'warning: ' + format.format(*args)
