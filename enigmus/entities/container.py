# coding=utf-8

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import enigmus

from core                import log
from core.messaging      import AsyncMessage
from entities.baseentity import BaseEntity

#-----------------------------------------------------------
# GLOBALS
#-----------------------------------------------------------

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Container(BaseEntity):
    def __init__(self):
        super(Container, self).__init__()

        self.entities = []

        self.on_messages('container_add'   , self.__on_container_add,
                         'container_remove', self.__on_container_remove,
                         'entity_cleanup'  , self.__on_entity_cleanup,
                         '*'               , self.__on_any_message)

    def add_entity(self, entity):
        self.post_message('container_add', self, entity)

    def get_entities(self, class_=BaseEntity):
        if not self.entities:
            return []

        return [e for e in self.entities if isinstance(e, class_)]

    def remove_entity(self, entity):
        self.post_message('container_remove', self, entity)

    def __on_container_add(self, container, entity):
        if entity.container:
            entity.container.remove_entity(entity)
            self.add_entity(entity)
            return

        entity.container = self
        self.entities.append(entity)

    def __on_container_remove(self, container, entity):
        self.entities.remove(entity)
        entity.container = None

    def __on_entity_cleanup(self):
        if self.entities:
            for entity in self.entities:
                entity.destroy()

            self.entities = None

    def __on_any_message(self, entity_id, msg, args):
        return
        if self.entities:
            print msg
            for entity in self.entities:
                entity.post_message(msg, *args)

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------
