# coding=utf-8

""" Provides language functionality. """

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------

def list(items):
    if len(items) == 1:
        return items[0]

    text = ', '.join([str(x) for x in items[:-1]]) + ' och ' + str(items[-1])

    return text

def sentence(text, *args):
    text = text.format(*args)
    text = text[0].upper() + text[1:]

    if text[-1] != '.':
        text += '.'

    return text
