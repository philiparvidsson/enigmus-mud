# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from cli                    import console
from core                   import log
from entities.commands.say  import SayCommand
from entities.commands.go  import GoCommand
from entities.commands.inventory  import TakeCommand
from entities.commands.inventory  import DropCommand
from entities.commands.inventory  import InventoryCommand
from entities.commands.look  import LookCommand
from entities.entity        import BaseEntity
from entities.actors.player import Player
from entities.room           import Room
from network.server         import TcpServer

import time

#-----------------------------------------------------------
# GLOBALS
#-----------------------------------------------------------

instance = None

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Enigmus(object):
    def __init__(self):
        self._done      = None
        self._msg_queue = None

        self.entities = None
        self.players  = None
        self.server   = None

    def cleanup(self):
        for entity in self.entities.values():
            entity.destroy()

        self.server.disconnect_all()
        self.server.stop_listening()

        self.entities = None
        self.players  = None
        self.server   = None

    def init(self):
        self._done      = False
        self._msg_queue = []

        self.entities = {}
        self.players  = []
        self.server   = TcpServer()

        self.server.on_messages([('connect'   , on_connect   ),
                                 ('disconnect', on_disconnect),
                                 ('receive'   , on_receive   )])

        self.server.listen('0.0.0.0', 1337)

    def post_message(self, target, msg, args):
        self._msg_queue.append((target, msg, args))

    def process_pending_messages(self):
        for target, msg, args in self._msg_queue:
            if target.id not in self.entities:
                log.warn('message dropped: {}, {}, {}', target.id, msg, args)

            for entity in self.entities.values():
                entity.handle_message(target, msg, args)

        self._msg_queue = []

    def register_entity(self, entity):
        if entity.id in self.entities:
            log.error('attempted to add entity {} twice', entity)
            return

        self.entities[entity.id] = entity
        print 'added entity {}'.format(entity.id)

    def remove_entity(self, entity):
        if not entity.id in self.entities:
            log.warn('cannot remove non-existent entity {}', entity)
            return

        del self.entities[entity.id]
        print 'removed entity {}'.format(entity.id)

    def tick(self, dt):
        for entity in self.entities.values():
            entity.tick(dt)

        self.server.update()

        self.process_pending_messages()

        if self._done:
            self.process_pending_messages()

        return not self._done

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------

'''def create_entity(class_, *args):
    if not issubclass(class_, BaseEntity):
        # TODO: Raise exception.
        print 'cant do dat'
        return None

    entity = class_(*args)

    instance.entities[entity.id] = entity


    return entity'''


def get_entity(id):
    return instance.entities[id]

def create_room(description):
    room = Room()
    room.description = description
    return room

def connect_rooms(room1, room2, exit1, exit2):
    room1.exits[exit1] = room2
    room2.exits[exit2] = room1

def exit():
    instance._done = True

def on_connect(connection):
    player = Player(connection)
    instance.players.append(player)

    connection.player = player

    print '{} connected.'.format(connection.address[0])

def on_disconnect(connection):
    connection.player.destroy()

    instance.players.remove(connection.player)

    print '{} disconnected.'.format(connection.address[0])

def on_receive(connection, data):
    connection.player.receive(data)

def run():
    global instance

    if instance is not None:
        print 'already running'
        return

    instance = Enigmus()

    instance.init()
    console.init()

    load_rooms()
    load_commands()
    load_actors()

    while instance.tick(1.0/5.0):
        console.update()
        time.sleep(1.0/5.0)

    instance.cleanup()

def load_commands():
    SayCommand()
    GoCommand()
    TakeCommand()
    DropCommand()
    InventoryCommand()
    LookCommand()

def load_rooms():
    room1 = create_room('Du står i ett konstigt rum. Det är inrett på ett homosexuellt vis. Du känner dig hemma.')
    room2 = create_room('Du finner dig själv i en liten trädgård med en fontän. Solen lyser på den blå himlen. Inifrån hörs glad bögmusik spelas. Någon kanske tittar på Melodifestivalen? Även dörren till köket (som går rätt ut, vad fan?) är öppen.')
    room3 = create_room('Du är nu i köket. Köket borde vara fullt av kvinnor som lagar mat, men spisen är avstängd och rummet fyllas av en ljuv tystnad.')
    room4 = create_room('Skamvrån. Vad gör du här? Vad skäms du för? En tanke slår dig; det kanske är du som är Bögen med stort B.')

    connect_rooms(room1, room2, 'ut', 'in')
    connect_rooms(room1, room3, 'kök', 'hall')
    connect_rooms(room3, room4, 'vrå', 'tillbaka')
    connect_rooms(room3, room2, 'ut', 'kök')


    def lol(room, entity):
        for e in room1.get_entities(Player):
            e.send('Det låter som att någon går runt i trädgården.')
    room2.on_message('room_enter', lol)

def load_actors():
    from entities.actors.mouse import Mouse
    from entities.actors.mouse import Flashlight
    mouse = Mouse()
    get_entity('Room_1').add_entity(mouse)

    fl = Flashlight()
    get_entity('Room_2').add_entity(fl)
