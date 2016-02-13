# coding=utf-8

""" Provides the base entity class. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus

from core import log
from core import messages

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class BaseEntity(object):
    """ Base class for all game entities. """

    _next_id = 1

    def __init__(self):
        """ Initializes the entity. """

        self.id = self.__class__.__name__ + '_' + str(BaseEntity._next_id)
        BaseEntity._next_id += 1

        self.container        = None
        self.description      = '<{}>'.format(self.__class__.__name__)
        self.is_destroyed     = False
        self.long_description = object.__str__(self)
        self.timers           = []

        self._msg_funcs = {}

        enigmus.instance.register_entity(self)

        self.on_message('entity_cleanup', self.__entity_cleanup)
        self.on_message('entity_destroy', self.__entity_destroy)
        self.on_message('entity_tick'   , self.__entity_tick   )

        self.post_message('entity_init')

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.get_description()

    def describe(self, *args):
        if len(args) == 1:
            # Probably a simple string description.
            self.description = args[0]
            return

        if len(args) == 2:
            self.description      = args[0]
            self.long_description = args[1]
            return

        indefinite = (args[0], args[1], args[2])
        definite   = (args[3], args[4], args[5])

        self.description = Description(indefinite, definite)

        if len(args) == 7:
            self.long_description = args[6]

    def destroy(self):
        """ Performs cleanup and destruction logic for the entity, and removes
            it from the game.
        """

        self.post_message('entity_cleanup')
        self.post_message('entity_destroy')

    def get_description(self, indefinite=True):
        """ Retrieves the entity description in definite or indefinite
            form.

            :param indefinite: Decides whether the returned description
                                 should be indefinite.

            :returns: The entity description.
        """
        if isinstance(self.description, basestring):
            # Simple string description.
            return self.description

        desc       = self.description.indefinite if indefinite else self.description.definite
        article    = desc[0]
        adjectives = [adjective for adjective in desc[1]]
        noun       = desc[2][0]

        s = '{} {} {}'.format(article, ' '.join(adjectives), noun)

        return s

    def handle_message(self, target, msg, args):
        """ Handles the specified message if it has been subscribed to by the
            entity.  The message will be ignored if the entity has been
            destroyed.

            :param target: The entity that the message was targeted at.
            :param msg:    The message.
            :param args:   The message arguments.
        """

        if self.is_destroyed:
            return

        if msg not in self._msg_funcs:
            return

        for func, filter in self._msg_funcs[msg]:
            if filter(target):
                func(*args)

    #---------------------------------------------------------------------------
    def _match_object(self, word, desc):
        object_index = 2

        match = 0
        for _tuple in desc:
            if word in _tuple[object_index]:
                if word == _tuple[object_index][0]:
                    match = 2
                else:
                    match = 1

                which_tuple = _tuple
                break
        else: # break not reached
            which_tuple = ('',[''],[''])

        return (match, which_tuple)

    def _match_quantifier(self, form_tuple, words):
        quantifier_index = 0
        quantifier = form_tuple[quantifier_index]

        if quantifier in words:
            check_first = quantifier == words[0] # if it exists, it must be first
            return (check_first, 1)
        else:
            return (True, 0) # no quantifier is ok

    def _match_adjectives(self, form_tuple, possible_adjectives):
        if len(possible_adjectives) == 0:
            return 0

        adjective_index = 1
        adjectives = form_tuple[adjective_index]

        match = 0
        for word in possible_adjectives:
            match = match + 1
            if not word in adjectives:
                match = -1
                break

        return match

    def match(self, text):
        """ Checks if the specified description matches the entity.
            :param description: The description to test against.
            :returns: True if the description matches the entity.
        """

        desc = self.description

        if isinstance(self.description, basestring):
            s = self.description.lower().split(' ')
            if len(s) == 1: desc = (('', [''], [s[0]]), ('', [''], [s[0]]))
            elif len(s) == 2: desc = ((s[0], [''], [s[1]]), (s[0], [''], [s[1]]))
            else: desc = ((s[0], s[1:-1], [s[-1]]), (s[0], s[1:-1], [s[-1]]))
        else:
            desc = ((desc.indefinite[0], desc.indefinite[1], desc.indefinite[2]),
                    (desc.definite[0], desc.definite[1], desc.definite[2]))

        text = text.lower()

        desc = ((desc[0][0].lower(), [x.lower() for x in desc[0][1]], [x.lower() for x in desc[0][2]]),
                (desc[1][0].lower(), [x.lower() for x in desc[1][1]], [x.lower() for x in desc[1][2]]))

        words = text.split(' ')
        n = len(words)
        last_index = n - 1

        (match_object, form) = self._match_object(words[last_index], desc)

        if n == 1:
            return match_object

        (match_quantifier, index_first_adjective) = self._match_quantifier(form, words)
        if not match_quantifier:
            return 0

        possible_adjectives = words[index_first_adjective : last_index]

        match_adjectives = self._match_adjectives(form, possible_adjectives)
        if match_adjectives == -1:
            return 0

        return match_object + match_adjectives
    #---------------------------------------------------------------------------

    def on_message(self, msg, func, filter=None):
        """ Subscribes a handler function for the specified message, using the
            specified filter.

            :param msg:    The message to subscribe to.
            :param func:   The message handler function.
            :param filter: The message filter to use.
        """

        if filter is None:
            filter = messages.for_entity(self)

        if msg not in self._msg_funcs:
            self._msg_funcs[msg] = []

        self._msg_funcs[msg].append((func, filter))

    def post_message(self, msg, *args):
        """ Posts a message targeted at the entity.

            :param msg:  The message to post.
            :param args: The message arguments.
        """

        enigmus.instance.post_message(self, msg, args)

    def tick(self, dt):
        """ Performs 'per-frame logic' for the entity.

            :param dt: The time delta, in seconds.
        """

        self.post_message('entity_tick', dt)

    def timer(self, func, interval, repeat=1):
        """  Creates a timer.

             :param func:     The timeout function.
             :param interval: The timer interval, in seconds.
             :param repeat:   The number of repetitions.
        """

        self.timers.append(Timer(func, interval, repeat))

    # ------- MESSAGES -------

    def __entity_cleanup(self):
        if self.container:
            self.container.remove_entity(self)

        self.timers = None

    def __entity_destroy(self):
        self.is_destroyed = True
        enigmus.instance.remove_entity(self)

    def __entity_tick(self, dt):
        for timer in self.timers:
            timer.tick(dt)

        for timer in [t for t in self.timers if t.finished]:
            self.timers.remove(timer)

class Description(object):
    def __init__(self, indefinite, definite):
        self.definite   = definite
        self.indefinite = indefinite

    def add_definite_adjective(self, adj, index=-1):
        if adj not in self.definite[1]: self.definite[1].insert(index, adj)

    def add_indefinite_adjective(self, adj, index=-1):
        if adj not in self.indefinite[1]: self.indefinite[1].insert(index, adj)

    def remove_definite_adjective(self, adj):
        if adj in self.definite[1]: self.definite[1].remove(adj)

    def remove_indefinite_adjective(self, adj):
        if adj in self.indefinite[1]: self.indefinite[1].remove(adj)

class Timer(object):
    """  Represents an entity timer. """

    def __init__(self, func, interval, repeat):
        """  Initializes the timer.

             :param func:     The timeout function.
             :param interval: The timer interval, in seconds.
             :param repeat:   The number of repetitions.
         """

        self.finished = False
        self.func     = func
        self.interval = interval
        self.repeat   = repeat
        self.time     = interval

    def tick(self, dt):
        """ Updates the timer.

            :param dt: The time delta, in seconds.
        """

        self.time -= dt

        if self.time > 0.0:
            return

        self.func()

        self.time = self.interval

        if self.repeat == 0:
            return # Timers with an initial repeat of zero will repeat forever.

        self.repeat -= 1
        if self.repeat <= 0:
            self.finished = True
