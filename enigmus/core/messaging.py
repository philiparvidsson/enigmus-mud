# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

#-----------------------------------------------------------
# GLOBALS
#-----------------------------------------------------------

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class AsyncMessage(object):
    def __init__(self, msg, args):
        self.args         = args
        self.msg          = msg
        self.result_funcs = []
        self.results      = None

    def on_result(self, func):
        if self.results:
            func(self.results)

        self.result_funcs.append(func)

    def result(self, r):
        self.results = r

        for func in self.result_funcs:
            func(r)

class MessageQueue(object):
    def __init__(self):
        self._msg_funcs = {}
        self._msg_queue = []

    def post_message(self, msg, *args):
        async = AsyncMessage(msg, args)

        self._msg_queue.append((async, msg, args))

        return async

    def process_pending_messages(self):
        for async, msg, args in self._msg_queue:
            results = []

            if '*' in self._msg_funcs:
                self._msg_funcs['*'](msg, args)

            if msg not in self._msg_funcs:
                async.result(results)
                continue

            for func in self._msg_funcs[msg]:
                r = func(*args)
                results.append(r)

            async.result(results)

        self._msg_queue = []

    def on_message(self, msg, func):
        if msg not in self._msg_funcs:
            self._msg_funcs[msg] = []

        self._msg_funcs[msg].append(func)

    def on_messages(self, msg_funcs):
        for msg, func in msg_funcs:
            self.on_message(msg, func)

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------
