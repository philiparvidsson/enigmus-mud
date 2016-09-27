# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

#import console
import database
import logging
import messages
import network

from entities import Actor
from entities import Container
from entities import ContainerItem
from entities import Entity
from entities import Item
from entities import Player
from entities import Room
from entities import WearableContainer
from entities import WearableItem

import time

#-----------------------------------------------------------
# CONSTANT
#-----------------------------------------------------------

QUESTS_DIR    = 'quests'
TICKS_PER_SEC = 10.0

#-----------------------------------------------------------
# GLOBALS
#-----------------------------------------------------------

instance = None

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Enigmus(object):
    def init(self):
        self.database = database.Database(QUESTS_DIR)
        self.entities = {}
        self.players  = []
        self.server   = network.TcpServer()

        self._done      = False
        self._msg_queue = []

        self.server.on_connect   (on_connect     )
        self.server.on_disconnect(on_disconnect  )
        self.server.on_receive   (on_receive     )
        self.server.listen       ('0.0.0.0', 1337)

    def cleanup(self):
        for entity in self.entities.values():
            entity.destroy()

        self.server.disconnect_all()
        self.server.stop_listening()

        self.entities = None
        self.players  = None
        self.server   = None

    def post_message(self, target, msg, args):
        self._msg_queue.append((target, msg, args))

    def process_pending_messages(self):
        for target, msg, args in self._msg_queue:
            if target and target.id not in self.entities:
                logging.warn('message dropped: {}, {}, {}', target.id, msg, args)

            for entity in self.entities.values():
                #try:
                    entity.handle_message(target, msg, args)
                #except Exception as e:
                #    logging.error('message {} ({}) for {} resulted in exception',
                #        msg, args, target)
                #    logging.error(str(e))

        self._msg_queue = []

    def register_entity(self, entity):
        if entity.id in self.entities:
            logging.error('attempted to add entity {} twice', entity)
            return

        self.entities[entity.id] = entity
        logging.info('created entity: {}', entity.id)

    def remove_entity(self, entity):
        if not entity.id in self.entities:
            logging.warn('cannot remove non-existent entity {}', entity)
            return

        del self.entities[entity.id]
        logging.info('destroyed entity: {}', entity.id)

    def tick(self, dt):
        self.post_message(None, 'tick', [dt])

        self.server.update()
        self.process_pending_messages()

        return not self._done

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------

def get_entity(id):
    return instance.entities[id]

def get_entity_class(name):
    return instance.database.get_class(name)

def exit():
    instance._done = True

def on_connect(connection):
    player = Player(connection)
    instance.players.append(player)

    connection.player = player

    logging.info('{} connected', connection.address[0])

def on_disconnect(connection):
    connection.player.destroy()

    instance.players.remove(connection.player)

    logging.info('{} disconnected', connection.address[0])

def on_receive(connection, data):
    connection.player.receive(data)

def run(quests):
    global instance
    instance = Enigmus()

    instance.init()
    #console.init()

    for quest in quests:
        instance.database.load_quest(quest)

    one_tick = 1.0/TICKS_PER_SEC
    cum_dt   = 0.0

    t1 = time.time()
    while not instance._done:
        t2      = time.time()
        cum_dt += t2 - t1
        t1      = time.time()

        while cum_dt >= one_tick:
            instance.tick(one_tick)
            cum_dt -= one_tick

        #console.update()
        time.sleep(one_tick/2.0)

    instance.cleanup()
