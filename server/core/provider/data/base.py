# -*- coding: utf-8 -*-

from sequence import Generator
class ActiveRecord():
    _table = None # this has to be set in the child class
    _data = {}
    _changedFields = {}
    row = None
    # values needed for generating the new sequence
    fillChar = None
    fillLength = 0

    def __init__(self):
        self._changedFields = {}
        self._data = {}
        self.row = None
        if self._table is None:
            self._table = self.__class__.__name__.lower()

    def __setitem__(self, name, value):
        if name.find(':') == -1:
            name += ':'
        self._changedFields[name] = 1
        self._data[name] = "%s" % value

    def __getitem__(self, name):
        if name.find(':') == -1:
            name += ':'
        return self._data[name]

    def __delitem__(self, name):
        if name.find(':') == -1:
            name += ':'
        del self._data[name]
        self._changedFields[name] = -1

    def __repr__(self):
        return "%s(%s)" % (self._table,self._changedFields)

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()

    def has_key(self, name):
        if name.find(':') == -1:
            name += ':'
        return self._data.has_key(name)

    def get(self, name, default=None):
        if name.find(':') == -1:
            name += ':'
        return self._data.get(name, default)

    def find(self, row):
        """
        Finds an element with the specified row and preloads the data.
        Notice: Implement this method in the child class.

        @param string row
        @return boolean
        """
        return None


    def findRange(self, startWith, endWith):
        """
        Finds list of elements that start with startWith key and and with the endWith key
        Notice: Implement this method in the child class.

        @param string startWith
        @param string endWith
        @return boolean
        """
        pass

    def setRow(self, row):
        """
        Sets the row key.

        @param string row
        """
        self.row = "%s" % row

    def save(self):
        """
        Save the data for the specified row.
        Notice: Implement this method in the child class.

        """
        if self.row is None and len(self._changedFields):
            self.row = Generator().get(self._table, self.fillChar, self.fillLength)

    def inc(self, key, value):
        """
        Increments a key.
        Notice: Implement this method in the child class.

        @param string key - key to increment
        @param int value - number to use
        """
        pass

    def delete(self):
        """
        Deletes a row.
        Notice: Implement this method in the child class.
        """
        pass

import core.pool.Redis as Redis
from core.pattern import Decorator
class CacheDecorator(Decorator):
    """
    Cache Decorator class for Active Record objects
    """

    def __init__(self, obj, expiration=86400, prefix='active_record_'):
        Decorator.__init__(self, obj)
        object.__setattr__(self, "redis", Redis.ConnectionPool().get())
	object.__setattr__(self, "expiration", expiration)
        prefix += "%s" % obj._table
        object.__setattr__(self, "prefix", prefix)

    def find(self, row):
        """
        Finds an element with the specified row and preloads the data.

        @param string row
        @return boolean
        """
        hashKey = "%s/%s" % (self.prefix , row)
        cache  = self.redis.hgetall(hashKey)
        if cache:
            self._obj.setRow(row)
            for (key, value) in cache.items():
                self._obj._data[key] = value
            return True

        if self._obj.find(row):
            # cache the data
            for (key, value) in self._obj.items():
                self.redis.hset(hashKey,key, value)
            return True

        return False

    def __getitem__(self, name):
        return self._obj[name]

    def __delitem__(self, name):
        del self._obj['name']

    def save(self):
        self._obj.save()
        self.redis.delete("%s/%s" % (self.prefix , self._obj.row))

    def delete(self):
        self.redis.delete("%s/%s" % (self.prefix , self._obj.row))

        return self._obj.delete()

    def __del__(self):
        # delete object references manually
        object.__delattr__(self, 'redis')
        Decorator.__del__(self)
