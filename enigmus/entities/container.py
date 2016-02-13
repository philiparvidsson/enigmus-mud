# coding=utf-8

""" Provides a container that can contain other entities. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

from core            import log
from entities.entity import BaseEntity

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Container(BaseEntity):
    """ Represents a container that can contain other entities. """

    def __init__(self):
        """ Initializes the container. """

        super(Container, self).__init__()

        self.entities = []

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

    def find_match(self, text):
        best_match = (0, None)

        for entity in self.entities:
            match = (entity.match(text), entity)
            if match[0] > best_match[0]:
                best_match = match

        return best_match[1]

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

    # ------- MESSAGES -------

    def __entity_cleanup(self):
        if not self.entities:
            return

        for entity in self.entities:
            entity.destroy()

        self.entities = None
