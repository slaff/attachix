# -*- coding: utf-8 -*-
import logger

class DummyCalendarProvider():
    def isCalendar(self, path, user=None):
        return True

    def store(self, path, event, user=None):
        pass

    def search(self, path, collectionType, objectType, properties, filter, user=None):
        logger.getLogger().debug("CollectionType: %s" % collectionType)
        logger.getLogger().debug("ObjectType: %s" % objectType)
        logger.getLogger().debug("Properties: %s" % properties)
        logger.getLogger().debug("Filter: %s" % filter)
        
        return {path:1}


