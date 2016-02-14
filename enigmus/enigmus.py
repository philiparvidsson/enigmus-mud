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

def load_room(data):
    room  = {}
    data  = data.replace('\r', '')
    lines = data.split('\n')

    room['description'] = ''
    room['details'    ] = []
    room['exits'      ] = []

    i = 0
    while i < len(lines):
        s = lines[i].strip()
        i += 1

        if s.startswith('!'):
            detail = s[1:].strip().split(':', 1)

            while s != '':
                s = lines[i].strip()
                i += 1
                detail[1] += s + ' '

            room['details'].append([detail[0].strip(), detail[1].strip()])
            pass
        elif s.startswith('#'):
            exit = s[1:].strip().split(' ', 1)
            room['exits'].append([exit[0].strip(), exit[1].strip()])
            pass
        else:
            if len(s) > 0:
                room['description'] += s + ' '

    room['description'] = room['description'].strip()

    return room

def load_rooms():
    import os
    import imp
    import json

    rooms = {}

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

        room              = Room()
        room.data         = room_data
        room.data['name'] = room_name
        rooms[room_name]  = room

    #-----------------------------------
    # 2. Setup rooms
    #-----------------------------------

    for room in rooms.values():
        room.describe(room.data['description'])

        for detail in room.data['details']:
            room.detail(detail[0],
                        detail[1])

        for exit in room.data['exits']:
            room.add_exit(      exit[0],
                          rooms[exit[1]])

        script_name = room.data['name'] + '_script'
        script_file = 'data/rooms/' + room.data['name'] + '.py'

        if os.path.isfile(script_file):
            script_module = imp.load_source(script_name, script_file)
            script_module.room = room
            script_module.init()

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

    room1 = rooms['room1']
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

    room2.describe('Du befinner dig längst ned i ett trapphus. Väggarna är vita och trappan är gjord av sten. Det finns ett svart räcke som följer trappan. Rummet är belyst av ett fönster längre upp i trappan.')
    room2.detail('ett fönster', 'Fönstret släpper in ljus i trapphuset, som i övrigt inte har några lampor. Genom fönstret kan man skymta en grå himmel utanför.')

    room3.describe('Du står i en korridor. Bredvid dig finns en datasal med glasdörrar. Dörrarna är låsta med ett litet kodlås. Framför dig ser du trappor som leder en våning upp. Det finns även toaletter i närheten för den som behöver uträtta sina behov.')
    room3.detail('ett kodlås', 'Det är en liten kodterminal för att trycka in koder med. Du förmodar att dörrarna till datasalen låses upp om man trycker in rätt kod.')
    room3.detail('en datasal', 'Du ser rätt in i datasalen som ligger innanför glasdörrarna. Om du bara kunde låsa upp dörren på något vis...')
    room3.detail('toaletter', 'En dörr leder in till toaletterna. Du kan gå in om du behöver uträtta dina behov.')

    def enter_code(player, command):
        args = command.split(' ')
        if args[0] != 'tryck': return
        if len(args) < 2 or args[1] != 'kod':
            player.send('Tryck vad? Kod?')
            return
        if len(args) < 3:
            player.send('Vilken kod vill du slå in?')
            return
        code = args[2]
        player.emote('slår in en kod.')
        player.text('*beep* *boop* *bip* piper terminalen när du trycker på knapparna och slår in koden {}'.format(code))
        if code != '4973':
            player.text('Ingenting händer.')
            return
        room = player.container
        for p in room.get_entities(Player):
            p.text('Glasdörrarna till datasalen slår upp så snabbt att du hoppar bakåt.')
        player.emote('går in i datasalen.')
        player.text('Glasdörrarna slår igen bakom dig.')
        room7.add_entity(player)
        player.text(room7.get_description(exclude_actor=player))
        for p in room.get_entities(Player):
            p.text('Lika snabbt som de öppnas slår dörrarna igen, alldeles för snabbt för att du skulle hinna gå in utan att vara beredd.')

    room3.on_message('player_command', enter_code, filter=messages.for_entities_in(room3))


    room4.describe('Du står i en korridor. Bredvid dig finns en stor ljussal. Det finns trappor här som leder en våning ner, till en korridor. Väggen här är av träpanel, medan golvet är av laminat.')

    room5.describe('Du står i en stor ljussal. Taket är säkert femton meter upp och av glas så att man ser himlen. Väggarna är vita, golvet är av svart laminat. Salen är fylld av trästolar och träbord som förmodligen är tänkta att ätas vid. Längst upp på ena väggen är flera fönster som leder in i andra rum i byggnaden. Rummen ser mörka och små ut härifrån. På den andra väggen kan du se en klocka. En öppen dörr med en skylt på leder in i ett annat rum.')
    room5.detail('en klocka', 'Det sitter en stor, gammaldags klocka ett par meter upp på väggen. Det är en gammal skolklocka. Den verkar ha stannat på 13:37. Lustigt!')
    room5.detail('ett fönster', 'Taket är mycket högt upp och av glas. Det är inte plant, utan format i flera små pyramider. Du förmodar tanken är att glastaket ska släppa in mycket ljus, men himlen utanför är så pass grå och mörk att belysningen ändå är ganska dov. Jösses, vilken mulen dag.')
    room5.detail('bord', 'Det är flera runda bord i rummet med stolar placerade runt dem.')
    room5.detail('stolar', 'Stolarna är noggrant placerade runt alla borden. En av stolarna står lite snett. Du undrar om någon använt den nyligen. Hmm...')
    room5.detail('rum', 'Rummen är i en annan del av byggnaden, men du kan skymta dem härifrån genom fönstrena längst upp på den ena väggen. Det är svårt att se in i dem eftersom de är så mörka. I ett av fönstrena tycker du dig kunna skymta ett ansikte som tittar ner på dig, men du får för dig att det bara är inbillning - att det egentligen bara är en kruka eller liknande som står i fönstret.')
    room5.detail('ett ansikte', 'I ett av fönstrena tycker du dig skymta ett ansikte. Det är helt orörligt och ser ut att stirra rätt ner i salen. Riktigt obehagligt!')
    room5.detail('skylt', 'På skylten står det: "Värm din mat här!"')

    room6.describe('Ett litet mörkt rum. Det luktar gammal mat i det här rummet. Runtom väggarna finns flera microvågsugnar utplacerade på hyllor. Väggarna är mörkturkos. Du ser en svart, rund soptunna i ett av rummets hörn.')
    room6.detail('en micro', 'Det är en vanlig microvågsugn. Den ser billig ut. Det finns gamla fastbrända matrester i den. Usch!')
    room6.detail('matrester', 'Någon har slarvat och struntat i att göra rent efter sig. Matresterna är nog micrade så pass många gånger att de i princip är omöjliga att få bort vid det här laget.')

    room7.describe('Du står i en datasal vid några glasdörrar. Datorer finns överallt, men alla verkar vara avstängda. Rummet är belyst av ett grönaktigt sken från alla de lysrör som sitter i taket. En soptunna står vid väggen bredvid dig.')
    room7.detail('datorer', 'Datasalen är fylld med säkert femtio datorer.')

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

    connect_rooms(room3, 'upp', 'upp för trapporna', 'nerifrån trapporna',
                  room4, 'ner', 'ner för trapporna', 'uppifrån trapporna')

    connect_rooms(room4, 'väster', 'västerut', 'österifrån',
                  room5, 'öster' , 'österut' , 'västerifrån')

    connect_rooms(room5, 'norr' , 'in i rummet', 'in i rummet',
                  room6, 'söder', 'ut ur rummet' , 'ut ur rummet')

    connect_rooms(room7, 'ut' , 'ut från datasalen', 'in genom glasdörrarna',
                  room3)

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
