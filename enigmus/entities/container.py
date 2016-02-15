# coding=utf-8

""" Provides a container that can contain other entities. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core            import log
from entities.entity import BaseEntity
from entities.item   import Item
from entities.item   import WearableItem

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Container(BaseEntity):
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
        self.is_open = False

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


    def get_entities(self, class_=BaseEntity):
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
        self.is_open = True

    def remove_entity(self, entity):
        """ Removes the entity from the container.

            :param entity: The entity to remove from the container.
        """

        if entity.container != self:
            log.warning('tried to remove entity from wrong container')
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

class ContainerItem(Container, Item):
    """ Represents a container item that can contain other entities. """

    def __init__(self):
        """ Initializes the container item. """

        super(ContainerItem, self).__init__()

#-------------------------------------------------------------------------------

class WearableContainer(WearableItem, Container):
    """ Represents a wearable item that can contain other entities. """

    def __init__(self):
        """ Initializes the wearable container. """

        super(WearableContainer, self).__init__()
