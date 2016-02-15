# coding=utf-8

""" Provides various filters for receiving entity messages. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------

def all():
    """ Receives all messages. """
    return lambda target: True

def for_actors_with_item(item):
    def filter(target):
        if not hasattr(target, 'inventory'):
            return False

        return target.inventory == item.container

    return filter

def for_entity(entity):
    """ Receives messages meant for the recipient.

        :param entity: The entity to receive messages for.
    """

    return lambda target: target == entity

def for_entities_in(container):
    """ Receives messages sent to a target inside the specified container.

        :param container: A container whose entities' messages will be received.
    """

    def filter(target):
        if target.container == container: return True
        if target           == container: return True

        return False

    return filter

def for_entities_of_class(class_):
    """ Receives messages sent to a target of the specified class.

        :param class_: The class of entities to receive messages for.
    """

    return lambda target: isinstance(target, class_)

def for_nearby_entities(entity):
    """ Receives messages sent to a target sharing container with the specified
        entity.

        :param entity: An entity sharing container with targets.
    """

    def filter(target):
        if not entity.container      : return False
        if entity.container == target: return True
        if not target.container      : return False

        return target.container == entity.container

    return filter

def none():
    """ Receives no messages. """

    return lambda target: False
