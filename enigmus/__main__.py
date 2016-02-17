# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus

import sys

#-----------------------------------------------------------
# SCRIPT
#-----------------------------------------------------------

if __name__ == '__main__':
    quest = ['common', 'demo']

    if len(sys.argv) < 2:
        print 'usage: python enigmus <quests>'
        print 'example: python enigmus common demo'
    else:
        enigmus.run(sys.argv[1:])
