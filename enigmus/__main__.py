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
    world = 'default'

    if len(sys.argv) < 2:
        print 'usage: python enigmus <worlds>'
        print 'example: python enigmus common default'
    else:
        enigmus.run(sys.argv[1:])
