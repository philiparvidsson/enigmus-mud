# coding=utf-8

""" Provides language functionality. """

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------

def list(items):
    if len(items) == 1:
        return items[0]

    # and
    text = ', '.join([str(x) for x in items[:-1]]) + ' och ' + str(items[-1])

    return text

def pronouns(observer, observed, *args):
    s = ''

    first_self  = True
    first_other = True
    for arg in args:
        if isinstance(arg, basestring):
            s += ' ' + arg
            continue

        if observer == observed:
            a = ' du' if first_self else ' dig'
            first_self = False
            s += a if observed == arg else ' ' + arg.get_description(indefinite=True)
        else:
            a = ' ' + sex(observed.sex) if observed and first_other else ' sig'
            first_other = False
            s += a if observed == arg else ' ' + arg.get_description(indefinite=True)

    return s.strip()

def sentence(text, *args):
    text = text.format(*args)
    text = text[0].upper() + text[1:]

    lc = text[-1]
    if lc != '.' and lc != '!' and lc != '?':
        text += '.'

    return text

def sex(s):
    return 'han' if s == 'male' else 'hon'

