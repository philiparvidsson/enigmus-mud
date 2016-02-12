# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus

from core import log
from core import messages

#-----------------------------------------------------------
# GLOBALS
#-----------------------------------------------------------

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class BaseEntity(object):
    _next_id = 1

    def __init__(self):
        self.id = self.__class__.__name__ + '_' + str(BaseEntity._next_id)
        BaseEntity._next_id += 1

        self.container   = None
        self.description = '<{}>'.format(self.__class__.__name__)
        self.timers      = []

        self._msg_funcs = {}

        self.on_messages('entity_cleanup', self.__on_entity_cleanup,
                         'entity_destroy', self.__on_entity_destroy,
                         'entity_tick'   , self.__on_entity_tick)

        self.post_message('entity_init')

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def destroy(self):
        self.post_message('entity_destroy')

    def on_message(self, msg, func, filter=None):
        if filter is None:
            filter = messages.for_entity(self)

        if msg not in self._msg_funcs:
            self._msg_funcs[msg] = []

        self._msg_funcs[msg].append((func, filter))

    def on_messages(self, *args):
        for i in xrange(0, len(args), 2):
            msg  = args[i]
            func = args[i+1]

            self.on_message(msg, func)

    def post_message(self, msg, *args):
        enigmus.instance.post_message(self, msg, args)

    def receive_message(self, target, msg, args):
        if msg not in self._msg_funcs:
            return

        for func, filter in self._msg_funcs[msg]:
            if filter(target):
                func(*args)

        if '*' in self._msg_funcs:
            for func, filter in self._msg_funcs['*']:
                if filter(target):
                    func(target, msg, args)

    def tick(self, dt):
        self.post_message('entity_tick', dt)

    def timer(self, func, timeout):
        self.timers.append(dict(func=func, timeout=timeout))

    def __on_entity_cleanup(self):
        if self.container:
            self.container.remove_entity(self)

        self.post_message('destroy')

    def __on_entity_destroy(self):
        enigmus.destroy_entity(self.id)

    def __on_entity_tick(self, dt):
        expired_timers = []

        for timer in self.timers:
            timer['timeout'] -= dt
            if timer['timeout'] < 0.0:
                expired_timers.append(timer)
                timer['func']()

        for timer in expired_timers:
            self.timers.remove(timer)
