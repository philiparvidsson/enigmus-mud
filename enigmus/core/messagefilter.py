# coding=utf-8

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------

def all():
    return lambda e: True

def default(entity):
    return lambda e: e.id == entity.id

def in_container(container):
    def filter(e):
        for entity in container.entities:
            if e.id == entity.id:
                return True
        return False

    return filter

def in_room(room):
    return in_container(room)

def in_same_container(entity):
    def filter(target):
        # Entity is not in a room.
        if not entity.container:
            return False

        # Target is a room.
        if entity.container.id == target.id:
            return True

        # Target is not in a room.
        if not target.container:
            return False

        # Container is shared?
        return target.container.id == entity.container.id

    return filter

def in_same_room(entity):
    return in_same_container(entity)

def none():
    return lambda e: False
