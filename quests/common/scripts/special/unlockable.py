# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import language
import messages

from entities import Actor, Container, Entity, Item

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Key(Item):
    def __init__(self):
        super(Key, self).__init__()

        self.key_name = None

class Unlockable(Entity):
    def __init__(self):
        super(Unlockable, self).__init__()

        self.is_locked = True
        self.key_name  = None

    def lock(self, key):
        if not isinstance(key, Key) : return False
        if key.key_name != self.key_name: return False

        self.is_locked = True
        self.post_message('unlockable_lock', self, key)
        return True

    def unlock(self, key):
        if not isinstance(key, Key) : return False
        if key.key_name != self.key_name: return False

        self.is_locked = False
        self.post_message('unlockable_unlock', self, key)
        return True

class UnlockableContainer(Container, Unlockable):
    def __init__(self):
        super(UnlockableContainer, self).__init__()

class LockCommands(Entity):
    def __init__(self):
        super(LockCommands, self).__init__()

        self.on_message('actor_lock', self.__actor_lock,
            filter=messages.for_entities_of_class(Actor))

        self.on_message('actor_unlock', self.__actor_unlock,
            filter=messages.for_entities_of_class(Actor))

        self.on_message('player_command', self.__player_command,
            filter=messages.for_actors_with_item_of_class(Key))

    def __actor_lock(self, actor, unlockable, key):
        actor.emote('låste', unlockable, 'med', key)

    def __actor_unlock(self, actor, unlockable, key):
        actor.emote('låste upp', unlockable, 'med', key)

    def __player_command(self, player, command):
        args    = command.split(' ')
        command = args[0]
        args    = args[1:]

        if command != 'lås':
            return

        unlock = False

        if len(args) > 0 and args[0] == 'upp':
            unlock = True
            args = args[1:]

        i = args.index('med') if 'med' in args else -1
        if i == -1:
            if unlock:
                player.text('Lås upp med vad?')
            else:
                player.text('Lås med vad?')
            return

        key_desc        = ' '.join(args[i+1:])
        unlockable_desc = ' '.join(args[:i])

        key = player.find_best_match(key_desc)
        if not key or not isinstance(key, Key):
            if unlock:
                player.text('Lås upp med vad?')
            else:
                player.text('Lås med vad?')
            return

        unlockable = player.find_best_match(unlockable_desc)
        if not unlockable and player.container:
            unlockable = player.container.find_best_match(unlockable_desc)

        if not unlockable or not isinstance(unlockable, Unlockable):
            if unlock:
                player.text('Lås upp vad?')
            else:
                player.text('Lås vad?')
            return

        if isinstance(unlockable, Container) and unlockable.is_open:
            player.text(language.sentence('Stäng {} först.', unlockable.get_description(indefinite=False)))
            return

        if unlock:
            if not unlockable.is_locked:
                player.text(language.sentence('{} är inte låst.', unlockable.get_description(indefinite=False)))
                return

            if not player.unlock(unlockable, key):
                player.emote('försöker låsa upp', unlockable, 'men misslyckas')
        else:
            if unlockable.is_locked:
                player.text(language.sentence('{} är redan låst.', unlockable.get_description(indefinite=False)))
                return

            if not player.lock(unlockable, key):
                player.emote('försöker låsa', unlockable, 'men misslyckas')


LockCommands()
