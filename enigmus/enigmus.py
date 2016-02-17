# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import console
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

import imp
import os
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
rooms    = {}
scripts  = {}

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Enigmus(object):
    def init(self):
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

def load_script(path, filename):
        name = os.path.join(path, filename)
        name = os.path.relpath(name, path)
        name = name.replace('\\', '/')

        if name in scripts:
            return scripts[name]

        script = imp.load_source(name.replace('.', '_'), os.path.join(path, filename))
        scripts[name] = script

        logging.info('loaded script: {}', name)

        return script

def load_scripts(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if not file.endswith('.py'):
                continue

            file = os.path.join(os.path.relpath(root, path), file)
            load_script(path, file)

def load_quest(path):
    path = os.path.join(QUESTS_DIR, path)

    load_scripts(os.path.join(path, 'scripts'))

    rooms = {}

    #-----------------------------------
    # 2. Load room data.
    #-----------------------------------

    for root, dirs, files in os.walk(os.path.join(path, 'rooms')):
        for file in files:
            file = os.path.join(root, file)
            if not file.endswith('.txt'):
                logging.warn('file {} ignored', file)
                continue

            name = os.path.basename(file[:file.find('.txt')])

            with open(file) as room_file:
                data = load_room(room_file.read())

            data['name'] = name
            rooms[name]  = data

    #-----------------------------------
    # 3. Create rooms, entities etc.
    #-----------------------------------

    for room_name, room_data in rooms.items():
        room = create_entity(room_data)
        room.data = room_data
        rooms[room_name] = room

    #-----------------------------------
    # 4. Setup exits.
    #-----------------------------------

    for room in rooms.values():
        for exit_data in room.data['exits']:
            room.add_exit(exit_data[0], rooms[exit_data[1]])

        # We're done with the room data here.
        del room.data

    globals()['rooms'].update(rooms)

def run(quests):
    global instance
    instance = Enigmus()

    instance.init()
    console.init()

    for quest in quests:
        load_quest(quest)

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

        console.update()
        time.sleep(one_tick/2.0)

    instance.cleanup()

def load_room(s):
    lines = s.replace('\r', '').split('\n')
    return load_data(lines)

def load_data(lines, indent_level=0):
    data = {}

    data['attributes'] = []
    data['long_desc' ] = ''
    data['details'   ] = []
    data['entities'  ] = []
    data['exits'     ] = []

    while len(lines) > 0:
        text = lines[0]

        if text.startswith('::') or text.strip().startswith('::'):
            lines.pop(0)
            continue

        if len(text) > 0 and not text.startswith('    ' * indent_level):
            return data

        text = text[4*indent_level:].strip()

        lines.pop(0)

        if len(text) == 0:
            continue

        if text.startswith('@'):
            data['script'] = text[1:].strip().split(':')

            if lines[0].startswith('    %'):
                data['attributes'] = []

                while len(text) > 0:
                    text = lines[0].strip()

                    if text.startswith('::') or text.strip().startswith('::'):
                        lines.pop(0)
                        continue

                    if not text.startswith('%'):
                        break

                    attribute = text[1:].split(':', 1)
                    data['attributes'].append([attribute[0].strip(), attribute[1].strip()])
                    lines.pop(0)

        elif text.startswith('%'):
            attribute = text[1:].split(':', 1)
            data['attributes'].append((attribute[0].strip(), attribute[1].strip()))
        elif text.startswith('!'):
            detail = text[1:].strip().split(':', 1)

            while len(text) > 0:
                if text.startswith('::') or text.strip().startswith('::'):
                    lines.pop(0)
                    continue

                text       = lines.pop(0).strip()
                detail[1] += ' ' + text

            data['details'].append((detail[0].strip(), detail[1].strip()))
        elif text.startswith('#'):
            exit = text[1:].strip().split(' ', 1)
            data['exits'].append((exit[0].strip(), exit[1].strip()))
        elif text.startswith('$'):
            script_data = text[1:].strip().split(':')

            indef_desc = None
            def_desc   = None

            s = lines[0].strip()
            if len(s) > 0 and not (s.startswith('!') or s.startswith('$') or s.startswith('$')):
                indef_desc  = [x for x in lines.pop(0).strip().split(' ') if x != '']
                def_desc    = [x for x in lines.pop(0).strip().split(' ') if x != '']

            entity_data = load_data(lines, indent_level+1)
            entity_data['script'] = script_data

            if indef_desc is not None and def_desc is not None:
                if len(indef_desc) == 3:
                    entity_data['indef_desc'] = (indef_desc[0], indef_desc[1].split('|'), indef_desc[2].split('|'))
                elif len(indef_desc) == 2:
                    entity_data['indef_desc'] = (indef_desc[0], [], indef_desc[1].split('|'))
                else:
                    entity_data['indef_desc'] = ('', [], indef_desc[0].split('|'))

                if len(def_desc) == 3:
                    entity_data['def_desc'] = (def_desc[0], def_desc[1].split('|'), def_desc[2].split('|'))
                elif len(def_desc) == 2:
                    entity_data['def_desc'] = (def_desc[0], [], def_desc[1].split('|'))
                else:
                    entity_data['def_desc'] = ('', [], def_desc[0].split('|'))

            data['entities'].append(entity_data)
        else:
            if len(text) > 0:
                data['long_desc'] += text + ' '

    data['long_desc'] = data['long_desc'].strip()

    return data

def get_entity_class(s):
    a = s.split(':')
    b = load_script(a[0])
    return getattr(b, a[1])

def create_entity(data):
    # TODO: This shit should be another function.
    if isinstance(data, basestring):
        a = data.split(':')
        b = load_script(a[0])
        c = getattr(b, a[1])
        return c()

    class_ = None

    if 'script' in data:
        if len(data['script']) == 2:
            script_name = data['script'][0]
            class_name  = data['script'][1]

            script_module = scripts[script_name]
            class_        = getattr(script_module, class_name)
        else:
            if   data['script'][0] == 'container'        : class_ = Container
            elif data['script'][0] == 'containeritem'    : class_ = ContainerItem
            elif data['script'][0] == 'item'             : class_ = Item
            elif data['script'][0] == 'wearablecontainer': class_ = WearableContainer
    else:
        # No script specified means it's a room without script.
        class_ = Room

    entity = class_()

    if 'def_desc' in data and 'indef_desc' in data:
        def_desc   = data['def_desc'  ]
        indef_desc = data['indef_desc']

        entity.describe(indef_desc[0], indef_desc[1], indef_desc[2],
                        def_desc  [0],   def_desc[1],   def_desc[2],
                        data['long_desc'])
    elif len(data['long_desc']) > 0:
        entity.describe(data['long_desc'])

    for detail_data in data['details']:
        entity.detail(detail_data[0], detail_data[1])

    for entity_data in data['entities']:
        e = create_entity(entity_data)
        if isinstance(entity, Actor):
            if isinstance(e, WearableItem):
                entity.wearables.append(e)
            else:
                entity.inventory.add_entity(e)
        else:
            entity.add_entity(e)

    for attribute_data in data['attributes']:
        val = attribute_data[1]
        if   val == 'false'                           : val = False
        elif val == 'true'                            : val = True
        elif val.startswith('"') and val.endswith('"'): val = val[1:-1]
        else                                          : val = float(val)

        setattr(entity, attribute_data[0], val)

    return entity
