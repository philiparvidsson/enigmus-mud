# coding=utf-8

""" Provides the take command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import imp
import logging
import os

from entities import Actor
from entities import Container
from entities import ContainerItem
from entities import Entity
from entities import Item
from entities import Player
from entities import Room
from entities import WearableContainer
from entities import WearableItem

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Database(object):
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.rooms    = {}
        self.scripts =  {}

    def save(entity):
        pass

    def create_entity(self, data):
        if isinstance(data, basestring):
            a = data.split(':')
            b = self.load_script(a[0])
            c = getattr(b, a[1])
            return c()

        class_ = None

        if 'script' in data:
            if len(data['script']) == 2:
                script_name = data['script'][0]
                class_name  = data['script'][1]

                script_module = self.scripts[script_name]
                class_        = getattr(script_module, class_name)
            else:
                if   data['script'][0] == 'container'        : class_ = Container
                elif data['script'][0] == 'containeritem'    : class_ = ContainerItem
                elif data['script'][0] == 'item'             : class_ = Item
                elif data['script'][0] == 'wearablecontainer': class_ = WearableContainer
                elif data['script'][0] == 'wearableitem'     : class_ = WearableItem
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
            e = self.create_entity(entity_data)
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

    def deserialize_entity(self, text):
        text = text.replace('\r', '')
        return self.parse_lines(text.split('\n'))

    def get_class(self, name):
        name = name.split(':')
        return getattr(self.scripts[name[0]], name[1])

    def load_script(self, path, filename):
            name = os.path.join(path, filename)
            name = os.path.relpath(name, path)
            name = name.replace('\\', '/')

            if name in self.scripts:
                return self.scripts[name]

            script = imp.load_source(name.replace('.', '_'), os.path.join(path, filename))
            self.scripts[name] = script

            logging.info('loaded script: {}', name)

            return script

    def load_scripts(self, path):
        for root, dirs, files in os.walk(path):
            for file in files:
                if not file.endswith('.py'):
                    continue

                file = os.path.join(os.path.relpath(root, path), file)
                self.load_script(path, file)

    def load_quest(self, quest):
        path = os.path.join(self.data_dir, quest)

        self.load_scripts(os.path.join(path, 'scripts'))

        rooms = {}

        #-----------------------------------
        # 1. Load room data.
        #-----------------------------------

        for root, dirs, files in os.walk(os.path.join(path, 'rooms')):
            for file in files:
                file = os.path.join(root, file)
                if not file.endswith('.txt'):
                    logging.warn('file {} ignored', file)
                    continue

                name = os.path.basename(file[:file.find('.txt')])

                with open(file) as room_file:
                    data = self.deserialize_entity(room_file.read())

                data['name'] = name
                rooms[name]  = data

        #-----------------------------------
        # 2. Create rooms, entities etc.
        #-----------------------------------

        for room_name, room_data in rooms.items():
            room = self.create_entity(room_data)
            room.data = room_data
            rooms[room_name] = room

        #-----------------------------------
        # 3. Setup exits.
        #-----------------------------------

        for room in rooms.values():
            for exit_data in room.data['exits']:
                room.add_exit(exit_data[0], rooms[exit_data[1]])

            # We're done with the room data here.
            del room.data

        self.rooms.update(rooms)

        logging.info('loaded quest: {}', quest)

    def parse_lines(self, lines, indent_level=0):
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

                entity_data = self.parse_lines(lines, indent_level+1)
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
