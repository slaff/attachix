# -*- coding: utf-8 -*-
import logging

class DummyCalendarProvider():
    def isCalendar(self, path, user=None):
        return True

    def store(self, path, event, user=None):
        pass

    def search(self, path, collectionType, objectType, properties, filter, user=None):
        logging.getLogger().debug("CollectionType: %s" % collectionType)
        logging.getLogger().debug("ObjectType: %s" % objectType)
        logging.getLogger().debug("Properties: %s" % properties)
        logging.getLogger().debug("Filter: %s" % filter)
        
        return {path:1}


