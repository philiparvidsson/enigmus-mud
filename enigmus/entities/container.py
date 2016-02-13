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

        self.on_message('container_add'   , self.__container_add   )
        self.on_message('container_remove', self.__container_remove)
        self.on_message('entity_cleanup'  , self.__entity_cleanup  )

    def add_entity(self, entity):
        """ Adds the specified entity to the container.

            :param entity: The entity to add.
        """

        self.post_message('container_add', self, entity)

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

        self.post_message('container_remove', self, entity)

    # ------- MESSAGES -------

    def __container_add(self, container, entity):
        if entity.container:
            # If the entity is already in a container, remove it from that
            # container first, then attempt to add it again.
            entity.container.remove_entity(entity)
            self.add_entity(entity)
            return

        entity.container = self
        self.entities.append(entity)

    def __container_remove(self, container, entity):
        self.entities.remove(entity)
        entity.container = None

    def __entity_cleanup(self):
        if not self.entities:
            return

        for entity in self.entities:
            entity.destroy()

        self.entities = None
