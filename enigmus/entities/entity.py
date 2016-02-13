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

        self.container    = None
        self.description  = '<{}>'.format(self.__class__.__name__)
        self.is_destroyed = False
        self.timers       = []

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

    def destroy(self):
        """ Performs cleanup and destruction logic for the entity, and removes
            it from the game.
        """

        self.post_message('entity_cleanup')
        self.post_message('entity_destroy')

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

    def matches(self, description):
        """ Checks if the specified description matches the entity.

            :param description: The description to test against.

            :returns: True if the description matches the entity.
        """

        # TODO: Come up with a better general matching technique.
        return self.description == description

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
