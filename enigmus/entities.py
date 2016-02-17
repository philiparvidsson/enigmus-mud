# coding=utf-8

""" Provides the base entity class. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus
import language
import logging
import messages

from session import Session

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Entity(object):
    """ Base class for all game entities. """

    _next_id = 1

    def __init__(self):
        """ Initializes the entity. """

        self.id = self.__class__.__name__ + '_' + str(Entity._next_id)
        Entity._next_id += 1

        self.container        = None
        self.description      = '<{}>'.format(self.__class__.__name__)
        self.details          = []
        self.is_destroyed     = False
        self.long_description = object.__str__(self)
        self.timers           = []

        self._msg_funcs = {}

        enigmus.instance.register_entity(self)

        self.on_message('entity_destroy', self.__entity_destroy)
        self.on_message('tick'          , self.__tick, filter=messages.all())

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

    def detail(self, description, long_description):
        detail = Detail(self)

        detail.describe(description, long_description)

        self.details.append(detail)

    def destroy(self):
        """ Performs cleanup and destruction logic for the entity, and removes
            it from the game.
        """

        self.post_message('entity_cleanup')
        self.post_message('entity_destroy')

    def find_best_match(self, text):
        matches = self.find_matches(text)

        if len(matches) == 0:
            return None

        return matches[0]

    def find_matches(self, text, keep_scores=False):
        matches = []

        for detail in self.details:
            match = (detail.match(text), detail)
            if match[0] > 0:
                matches.append(match)

        matches = sorted(matches, key=lambda x: x[0], reverse=True)
        if keep_scores:
            return matches

        return [x[1] for x in matches]

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


        if len(adjectives) > 0:
            s = '{0} {1} {2}' if len(article) > 0 else '{1} {2}'
        else:
            s = '{0} {2}' if len(article) > 0 else '{2}'

        return s.format(article, ' '.join(adjectives), noun)

    def get_long_description(self):
        return self.long_description

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
            if   len(s) == 1: desc = ((  '', [''], [s[0]]), (  '', [''], [s[0]]))
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

        return match_object + match_adjectives + 1
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

    def timer(self, func, interval, args=None, repeat=1):
        """  Creates a timer.

             :param func:     The timeout function.
             :param interval: The timer interval, in seconds.
             :param repeat:   The number of repetitions.
        """

        self.timers.append(Timer(args, func, interval, repeat))

    # ------- MESSAGES -------

    def __entity_destroy(self):
        self.timers = None

        if self.container:
            self.container.remove_entity(self)

        self.is_destroyed = True
        enigmus.instance.remove_entity(self)

    def __tick(self, dt):
        for timer in self.timers:
            timer.tick(dt)

        for timer in [t for t in self.timers if t.finished]:
            self.timers.remove(timer)

#-------------------------------------------------------------------------------

class Actor(Entity):
    """ Represents an actor entity. """

    def __init__(self):
        """ Initializes the actor. """

        super(Actor, self).__init__()

        self.inventory = Inventory(10, self)
        self.sex       = 'male'
        self.wearables = []

        self.on_message('actor_drop'    , self.__actor_drop    )
        self.on_message('actor_give'    , self.__actor_give    )
        self.on_message('actor_go'      , self.__actor_go      )
        self.on_message('actor_remove'  , self.__actor_remove  )
        self.on_message('actor_wear'    , self.__actor_wear    )
        self.on_message('entity_cleanup', self.__entity_cleanup)

    def close(self, container):
        if not container.close():
            return False

        self.post_message('actor_close', self, container)
        return True

    def drop(self, item, container=None):
        """ Drops the specified item from the actor's inventory into the
            specified container.

            :param item:      The item to drop.
            :param container: The container to drop the item into.

            :returns: True if the item was dropped successfully.
        """

        if not container and not self.container: return False
        if item.container != self.inventory    : return False

        if not container:
            container = self.container

        self.post_message('actor_drop', self, container, item)
        return True

    def find_matches(self, text, keep_scores=False):
        matches = super(Actor, self).find_matches(text, keep_scores=True)

        matches.extend(self.inventory.find_matches(text, keep_scores=True))

        for wearable in self.wearables:
            match = (wearable.match(text), wearable)
            if match[0] > 0:
                matches.append(match)

        matches = sorted(matches, key=lambda x: x[0], reverse=True)
        if keep_scores:
            return matches

        return [x[1] for x in matches]

    def emote(self, *args):
        self.post_message('actor_emote', self, args)

    def get_long_description(self, observer=None):
        if not observer:
            observer = self

        desc = super(Actor, self).get_long_description()

        if len(self.wearables) > 0:
            wearable_descs = [x.get_description() for x in self.wearables]
            # {} is wearing {}.
            desc += '\n' + language.sentence(language.pronouns(observer, self, self, 'har', language.list(wearable_descs), 'på', self))

        return desc

    def give(self, actor, item):
        """ Gives the specified item to the specified actor.

            :param actor: The actor to give an item to.
            :param item:  The item to give.

            :returns: True if the item was given successfully.
        """

        if item.container != self.inventory : return False
        if actor.container != self.container: return False

        self.post_message('actor_give', self, actor, item)
        return True

    def go(self, direction):
        """ Exits the room through the specified exit.

            :param direction: The exit to leave the room through.

            :returns: True if the room was exited successfully.
        """


        room = self.container

        #if not isinstance(room, Room): return False # TODO: Circular dependency.
        if direction not in room.exits: return False

        self.post_message('actor_go', direction)
        return True

    def match(self, text):
        """ Checks if the specified description matches the entity.

            :param description: The description to test against.

            :returns: True if the description matches the entity.
        """

        if text == 'alla':
            return 1

        return super(Actor, self).match(text)

    def open(self, container):
        if not container.open():
            return False

        self.post_message('actor_open', self, container)
        return True

    def remove(self, wearable):
        if not wearable in self.wearables: return False

        self.post_message('actor_remove', self, wearable)
        return True

    def say(self, text, target=None):
        """ Says the specified text to the specified target.

            :param text:   The sentence to say.
            :param target: The entity to say it to.
        """

        self.post_message('actor_say', self, text, target)

    def take(self, item):
        """ Attempts to take the specified item.

            :param item: The item to take.

            :returns: True if the item was taken successfully.
        """

        if not isinstance(item, Item)                     : return False
        if hasattr(item, 'takeable') and not item.takeable: return False

        container = item.container

        self.inventory.add_entity(item)
        self.post_message('actor_take', self, container, item)

        return True

    def wear(self, wearable):
        if wearable.container != self.inventory  : return False
        if wearable in self.wearables            : return False
        if not isinstance(wearable, WearableItem): return False

        self.post_message('actor_wear', self, wearable)
        return True

    # ------- MESSAGES -------

    def __actor_drop(self, actor, container, item):
        container.add_entity(item)

    def __actor_give(self, giver, receiver, item):
        self.inventory.remove_entity(item)
        receiver.inventory.add_entity(item)

    def __actor_go(self, direction):
        room = self.container

        exit     = room.exits[direction]
        new_room = exit[0]

        room.remove_entity(self)
        self.post_message('actor_leave', self, room, exit[1])

        new_room.add_entity(self)
        self.post_message('actor_enter', self, new_room, exit[2])

    def __actor_remove(self, actor, wearable):
        self.wearables.remove(wearable)
        self.inventory.add_entity(wearable)

    def __actor_wear(self, actor, wearable):
        self.inventory.remove_entity(wearable)
        self.wearables.append(wearable)

    def __entity_cleanup(self):
        if not self.inventory:
            return

        for item in self.inventory.entities:
            self.drop(item)

        self.inventory.destroy()
        self.inventory = None

#-------------------------------------------------------------------------------

class Player(Actor):
    MAX_BUFFER = 1024

    def __init__(self, connection):
        super(Player, self).__init__()

        self._buffer = ''
        self._connection = connection

        self.session = Session(self)

        self.on_message('player_command', self.__on_player_command)
        self.on_message('player_text', self.__player_text)

    def disconnect(self):
        self._connection.close()

    def receive(self, text):
        self._buffer += text.decode('iso-8859-1').encode('utf-8')

        if len(self._buffer) > Player.MAX_BUFFER:
            self.disconnect()
            return

        i = self._buffer.find('\n')
        if i == -1:
            return None

        command = self._buffer[:i]
        self._buffer = self._buffer[i+1:]

        i = command.find('\r')
        if i >= 0:
            command = command[:i]

        self.session.state.handle_command(command)

    def send(self, text, end='\n', hard_breaks=True):
        text = text.replace('\r', '')
        s    = ''

        while len(text) > 0:
            last_space = 0
            linebreak  = False
            counter    = 0

            for i in xrange(len(text)):
                if text[i] == ' ':
                    last_space = i
                elif text[i] == '\n':
                    counter = 0

                if hard_breaks and counter >= 80:
                    if last_space == 0:
                        s   += text[:80] + '\n'
                        text = text[80:]
                    else:
                        s   += text[:last_space] + '\n'
                        text = text[last_space+1:]

                    linebreak = True
                    break

                counter += 1

            if not linebreak:
                s   += text
                text = ''

        s   = s  .replace('\n', '\r\n')
        end = end.replace('\n', '\r\n')

        self._connection.send(s  .decode('utf-8').encode('iso-8859-1'))
        self._connection.send(end.decode('utf-8').encode('iso-8859-1'))

    def text(self, text):
        self.post_message('player_text', text)

    def __on_player_command(self, player, command):
        if player is not self:
            return False

        args = command.split(' ')

    def __player_text(self, text):
        self.send(text)

#-------------------------------------------------------------------------------

class Container(Entity):
    """ Represents a container that can contain other entities. """

    def __init__(self):
        """ Initializes the container. """

        super(Container, self).__init__()

        self.entities = []
        self.is_open  = True

        self.on_message('entity_cleanup'  , self.__entity_cleanup  )

    def add_entity(self, entity):
        """ Adds the specified entity to the container.

            :param entity: The entity to add.
        """

        if entity.container:
            # If the entity is already in a container, remove it from that
            # container first, then attempt to add it again.
            entity.container.remove_entity(entity)
            self.add_entity(entity)
            return

        entity.container = self
        self.entities.append(entity)
        self.post_message('container_add', self, entity)

    def close(self):
        """ Closes the container. """

        self.is_open = False
        self.post_message('container_close', self)

        return True

    def find_matches(self, text, keep_scores=False):
        matches = super(Container, self).find_matches(text, keep_scores=True)

        for entity in self.entities:
            match = (entity.match(text), entity)
            if match[0] > 0:
                matches.append(match)

            # Also match against the entities details since they are on the
            # 'outside' of it.
            for detail in entity.details:
                match = (detail.match(text), detail)
                if match[0] > 0:
                    matches.append(match)

        matches = sorted(matches, key=lambda x: x[0], reverse=True)
        if keep_scores:
            return matches

        return [x[1] for x in matches]


    def get_entities(self, class_=Entity):
        """ Retrieves all entities of the specified class inside the container.

            :param class_: The class of entities to return.
        """

        if not self.entities:
            return []

        return [x for x in self.entities if isinstance(x, class_)]

    def is_empty(self):
        """ Checks if the container is empty.

            :returns: True if the container is empty.
        """

        return len(self.entities) == 0

    def open(self):
        """ Opens the container. """

        self.is_open = True
        self.post_message('container_open', self)

        return True

    def remove_entity(self, entity):
        """ Removes the entity from the container.

            :param entity: The entity to remove from the container.
        """

        if entity.container != self:
            logging.warning('tried to remove entity from wrong container')
            return

        if self.entities:
            self.entities.remove(entity)

        entity.container = None

        self.post_message('container_remove', self, entity)

    # ------- MESSAGES -------

    def __entity_cleanup(self):
        if not self.entities:
            return

        for entity in self.entities:
            entity.destroy()

        self.entities = None

#-------------------------------------------------------------------------------

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

#-------------------------------------------------------------------------------

class Detail(Entity):
    def __init__(self, entity):
        super(Detail, self).__init__()

        self.entity = entity

#-------------------------------------------------------------------------------

class Inventory(Container):
    """ Represents an actor inventory. """

    def __init__(self, actor, max_entities):
        """ Initializes the inventory.

            :param actor:        The inventory owner.
            :param max_entities: The max number of entities allowed.
        """

        super(Inventory, self).__init__()

        self.actor        = actor
        self.max_entities = max_entities

        self.on_message('entity_cleanup', self.__entity_cleanup)

    # ------- MESSAGES -------

    def __entity_cleanup(self):
        if not self.entities:
            return

        for item in self.entities:
            item.destroy()

        self.entities = None

#-------------------------------------------------------------------------------

class Room(Container):
    """ Represents a room with entities. """

    def __init__(self):
        """ Initializes the room. """

        super(Room, self).__init__()

        self.description = '<{} is missing a description>'.format(self.id)
        self.exits       = {}

    def add_exit(self, exit, room):
        self.exits[exit] = (room, '', '')

    def get_description(self, exclude_actor=None):
        """ Retrieves a description of the room.

            :returns: A description of the room, including its exits, any actors
                      in the room and any items in it.
        """

        room_desc  = language.sentence(super(Room, self).get_description())
        exits_desc = language.list(self.exits.keys()) if len(self.exits) > 0 else 0

        # {}\nExits: {}
        desc = '{}\nUtgångar: {}'.format(room_desc, exits_desc)

        actors = self.get_entities(Actor)
        if exclude_actor in actors:
            actors.remove(exclude_actor)
        if len(actors) > 0:
            # {} are here.
            desc += '\n' + language.sentence('{} är här.', language.list(actors))

        items = self.get_entities(Item)
        if len(items) > 0:
            desc += '\n' + language.sentence('{}', language.list(items))

        return desc

#-------------------------------------------------------------------------------

class Timer(object):
    """  Represents an entity timer. """

    def __init__(self, args, func, interval, repeat):
        """  Initializes the timer.

             :param func:     The timeout function.
             :param interval: The timer interval, in seconds.
             :param repeat:   The number of repetitions.
         """

        self.args     = args
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

        if self.args:
            self.func(*self.args)
        else:
            self.func()

        self.time = self.interval

        if self.repeat == 0:
            return # Timers with an initial repeat of zero will repeat forever.

        self.repeat -= 1
        if self.repeat <= 0:
            self.finished = True

#-------------------------------------------------------------------------------

class Item(Entity):
    """ Represents an item in the game. """

    def match(self, text):
        """ Checks if the specified description matches the entity.

            :param description: The description to test against.

            :returns: True if the description matches the entity.
        """

        if text == 'allt':
            return 1

        return super(Item, self).match(text)

#-------------------------------------------------------------------------------

class ContainerItem(Container, Item):
    """ Represents a container item that can contain other entities. """

    def __init__(self):
        """ Initializes the container item. """

        super(ContainerItem, self).__init__()

#-------------------------------------------------------------------------------

class WearableItem(Item):
    """ Represents a wearable item in the game. """
    pass

#-------------------------------------------------------------------------------

class WearableContainer(WearableItem, Container):
    """ Represents a wearable item that can contain other entities. """

    def __init__(self):
        """ Initializes the wearable container. """

        super(WearableContainer, self).__init__()
