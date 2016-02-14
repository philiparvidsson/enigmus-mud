# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from cli                    import console
from core                    import messages
from core                   import log
from entities.commands.say  import SayCommand
from entities.commands.go  import GoCommand
from entities.commands.take  import TakeCommand
from entities.commands.drop  import DropCommand
from entities.commands.inventory  import InventoryCommand
from entities.commands.give  import GiveCommand
from entities.commands.look  import LookCommand
from entities.commands.quit  import QuitCommand
from entities.commands.emotes  import EmoteHandler
from entities.commands.help  import HelpCommand
#from entities.commands.emote  import KissCommand
from entities.entity        import BaseEntity
from entities.item        import Item
from entities.container        import Container
from entities.container        import ContainerItem
from entities.actor import BaseActor
from entities.actors.player import Player
from entities.room           import BaseRoom
from network.server         import TcpServer

import imp
import os
import time

#-----------------------------------------------------------
# GLOBALS
#-----------------------------------------------------------

rooms   = {}
scripts = {}
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
                #try:
                    entity.handle_message(target, msg, args)
                #except Exception as e:
                #    log.error('message {} ({}) for {} resulted in exception',
                #        msg, args, target)
                #    log.error(str(e))

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
    room.describe(description)
    return room

def connect_rooms(room1, exit1, exit_desc1, exit_desc2, room2, exit2=None, exit_desc3=None, exit_desc4=None):
    room1.exits[exit1] = (room2, exit_desc1, exit_desc2)
    if exit2 is not None:
        room2.exits[exit2] = (room1, exit_desc3, exit_desc4)

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
    EmoteHandler()
    SayCommand()
    GoCommand()
    TakeCommand()
    DropCommand()
    InventoryCommand()
    LookCommand()
    GiveCommand()
    QuitCommand()
    HelpCommand()

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

        if len(text) > 0 and not text.startswith('    ' * indent_level):
            return data

        text = text[4*indent_level:].strip()

        lines.pop(0)

        if text.startswith('@'):
            data['script'] = text[1:].strip().split(':')
        elif text.startswith('%'):
            attribute = text[1:].split(':', 1)
            data['attributes'].append((attribute[0].strip(), attribute[1].strip()))
        elif text.startswith('!'):
            detail = text[1:].strip().split(':', 1)

            while len(text) > 0:
                text       = lines.pop(0).strip()
                detail[1] += text + ' '

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
                entity_data['indef_desc'] = (indef_desc[0], indef_desc[1].split('|'), indef_desc[2].split('|'))
                entity_data['def_desc'  ] = (def_desc[0], def_desc[1].split('|'), def_desc[2].split('|'))

            data['entities'].append(entity_data)
        else:
            if len(text) > 0:
                data['long_desc'] += text + ' '

    data['long_desc'] = data['long_desc'].strip()

    return data

def load_script(filename):
        script_name = '_script' + filename[:filename.index('.py')]

        if script_name in scripts:
            return scripts[script_name]

        script_module = imp.load_source(script_name, 'data/scripts/' + filename)
        scripts[script_name] = script_module

        print 'loaded script', filename

        return script_module

def create_entity(data):
    class_ = None

    if 'script' in data:
        if len(data['script']) == 2:
            script_name = data['script'][0]
            class_name  = data['script'][1]

            script_module = load_script(script_name)
            class_        = getattr(script_module, class_name)
        else:
            if   data['script'][0] == 'container': class_ = Container
            elif data['script'][0] == 'item'     : class_ = Item
    else:
        # No script specified means it's a room without script.
        class_ = BaseRoom

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
        if isinstance(entity, BaseActor):
            entity.inventory.add_entity(create_entity(entity_data))
        else:
            entity.add_entity(create_entity(entity_data))

    return entity

def load_rooms():
    #-----------------------------------
    # 1. Load rooms
    #-----------------------------------

    for filename in os.listdir('data/rooms'):
        if not filename.endswith('.txt'):
            continue

        room_name = filename[:filename.find('.txt')]
        filename  = 'data/rooms/' + filename

        with open(filename) as room_file:
            room_data = load_room(room_file.read())

        room_data['name'] = room_name
        rooms[room_name]  = room_data

    #-----------------------------------
    # 2. Setup rooms, entitites etc.
    #-----------------------------------

    for room_name, room_data in rooms.items():
        room = create_entity(room_data)
        room.data = room_data
        rooms[room_name] = room

    #-----------------------------------
    # 3. Setup exits.
    #-----------------------------------

    for room in rooms.values():
        for exit_data in room.data['exits']:
            room.add_exit(exit_data[0], rooms[exit_data[1]])

        del room.data

    ''' room1 = Room()
    room2 = Room()
    room3 = Room()
    room4 = Room()

    room1.describe('Du står i ett konstigt rum. Det är inrett på ett homosexuellt vis. Du känner dig SOM hemma. Förbannat som hemma. Dessutom hänger det en sexgunga i taket.')
    room1.detail('ett tak', 'Det är ett vitt tak. Det hänger en sexgunga i det.')
    room1.detail('en sexgunga', 'En sexgunga i svartläder. Där stjärten planceras sitter det en dildo. Det ser ut som man kan ha riktigt trevligt här. Om man är bög. Och det är du. En bög. Japp.')

    room2.describe('Du finner dig själv i en liten trädgård med en fontän. Solen lyser på den blå himlen. Inifrån hörs glad bögmusik spelas. Någon kanske tittar på Melodifestivalen? Även dörren till köket (som går rätt ut, vad fan?) är öppen.')
    room2.detail('en fontän', 'Det är en liten, vit marmorfontän. Jävlar vad den sprutar. Den får dig att tänka snuskiga tankar, så du slutar genast titta på den och låtsas som ingenting.')
    room2.detail('solen', 'Den lyser utav bara helvete.')

    room3.describe('Du är nu i köket. Köket borde vara fullt av kvinnor som lagar mat, men spisen är avstängd och rummet fyllas av en ljuv tystnad.')
    room3.detail('tystnad', 'Det är helt jävla knäpptyst. Inte ett luder som kacklar. Fyfan vad skönt, tänker du.')

    room4.describe('Skamvrån. Vad gör du här? Vad skäms du för? En tanke slår dig; det kanske är du som är Bögen med stort B. Någon har ristat in en text på väggen.')
    room4.detail('en text', 'Någon har ristat in text på väggen med ett vasst föremål. Det står: "DEN SOM LÄSER DETTA ÄR GAY"')

    connect_rooms(room1, 'ut', 'ut', 'ut',
                  room2, 'in', 'in', 'in')

    connect_rooms(room1, 'kök',  'in i köket' , 'in från hallen',
                  room3, 'hall', 'ut i hallen', 'ut från köket')

    connect_rooms(room3, 'vrå'     , 'in i skamvrån'   , 'in från köket',
                  room4, 'tillbaka', 'ut från skamvrån', 'in från skamvrån')

    connect_rooms(room3, 'ut' , 'ut i trädgården' , 'ut från hallen',
                  room2, 'kök', 'in i köket'      , 'in från trändgården')


    def lol(room, entity):
        for e in room1.get_entities(Player):
            e.send('Det låter som att någon går runt i trädgården.')
    room2.on_message('container_add', lol)'''
    return

    '''room1 = rooms['room1']
    room2 = Room()
    room3 = Room()
    room4 = Room()
    room5 = Room()
    room6 = Room()
    room7 = Room()

    #room1.describe('Du befinner dig i en stor entrésal. Taket är flera meter högt upp, golvet är av svart laminat och väggarna är vitmålade. En tavla sitter på väggen framför dig, och till vänster sitter några TV-skärmar på väggen och flimrar. Rakt fram fortsätter salen mot en korridor, även den med lika högt i tak. Till höger finns glasdörrar som går in till ett trapphus.')
    #room1.detail('skärmar', 'Skärmarna flimrar och visar bara brus för tillfället.')
    #room1.detail('en tavla', 'Det ser ut som ett inglasat diplom av något slag. Det finns lite text på tavlan, men den går inte att läsa. Du känner däremot att du har koll på hur man tittar föremål. Det känns väl bra?')
    #room1.detail('en text', 'Texten på tavlan är svårläst. Du kan inte riktigt tyda den.')
    #room1.detail('ett trapphus', 'Innanför glasdörren syns ett trapphus. Du kan gå dit om du vill.')



    room6.describe('')
    room6.detail('en micro', '')
    room6.detail('matrester', '')

    room7.describe('')
    room7.detail('datorer', '')

    trashcan = Container()
    trashcan.describe('en' , ['svart'] , ['soptunna' , 'tunna'],
                      'den', ['svarta'], ['soptunnan', 'tunnan'],
                      'Soptunnan är rund och svart. Den är gjord av billig glansig plast och verkar ganska ömtålig för att vara soptunna. Trots det förefaller den fylla sin funktion eftersom man åtminstone kan stoppa saker i den.')
    room7.add_entity(trashcan)

    note = Item()
    note.describe('en' , ['gul' ], ['lapp', 'lappar' ],
                  'den', ['gula'], ['lappen'         ],
                  'En liten skrynklig lapp som någon försökt göra sig av med en gång i tiden. På lappen står det skrivet med stora siffror: "4973"')

    tissue = Item()
    tissue.describe('en' , ['äcklig' ], ['näsduk'  ],
                    'den', ['äckliga'], ['näsduken'],
                    'En ihopskrynklad vit pappersnäsduk. Tänk om någon har snytit sig i den? Usch!')

    trashcan = Container()
    #trashcan.takeable = False
    trashcan.describe('en' , ['svart'] , ['soptunna' , 'tunna'],
                      'den', ['svarta'], ['soptunnan', 'tunnan'],
                      'Soptunnan är rund och svart. Den är gjord av billig glansig plast och verkar ganska ömtålig för att vara soptunna. Trots det förefaller den fylla sin funktion eftersom man åtminstone kan stoppa saker i den.')

    trashcan.add_entity(note)
    trashcan.add_entity(tissue)

    backpack = ContainerItem()
    backpack.describe('en' , ['grå'], ['ryggsäck'  ],
                      'den', ['grå'], ['ryggsäcken'],
                      'Det är en grå ryggsäck.')

    room2.add_entity(backpack)
    room6.add_entity(trashcan)

    #connect_rooms(room1, 'norr' , 'norrut' , 'söderifrån',
    #              room3, 'söder', 'söderut', 'norrifrån')

    #connect_rooms(room1, 'öster' , 'österut' , 'västerifrån',
    #              room2, 'väster', 'västerut', 'österifrån')

    connect_rooms(room5, 'norr' , 'in i rummet', 'in i rummet',
                  room6, 'söder', 'ut ur rummet' , 'ut ur rummet')

    connect_rooms(room7, 'ut' , 'ut från datasalen', 'in genom glasdörrarna',
                  room3)'''

def load_actors():
    '''from entities.actors.mouse import Mouse
    from entities.actors.mouse import Flashlight
    from entities.actors.mouse import MattPresent
    mouse = Mouse()
    get_entity('Room_1').add_entity(mouse)

    fl = Flashlight()
    get_entity('Room_2').add_entity(fl)

    mp = MattPresent()
    get_entity('Room_4').add_entity(mp)'''
