# [ Authentication Backends ] #
import logging
import os

CLEAR_TEXT=1
MD5_HASH  =2
OTHER     =3

class AbstractBackend():
    passwordStorage = CLEAR_TEXT # specifies if the passwords are kept in clear text

    def passHash(self, username, password, realm):
        return password;

    def load(self):
        pass

    def check(self, username, password, realm):
        """
        Checks if there is a user with the specified username and password for the specified realm
        @param string username
        @param string password in clear text
        @return boolean
        """
        return self.get(username) == self.passHash(username, password, realm)

    def has_key(self, key):
        pass

    def get(self, key, defaultValue=None):
        try:
            return self._get(key)
        except KeyError:
            return defaultValue

    def __getitem__(self, key):
        if isinstance(key, slice):
            raise ValueError("The key cannot be slice")

        return self._get(key)

    def _get(self, key):
        raise Exception("Implement this method in the child class")


class FileBackend(AbstractBackend):
    data = {}
    modified = None

    def __init__(self, file, delimiter=":"):
        self.file = file
        self.delimiter = delimiter
        self.data = {}

    def load(self):
        stats = os.stat(self.file)
        if stats.st_mtime == self.modified:
            return

        logging.getLogger().debug("Loading auth data")
        self.modified = stats.st_mtime

        f = open(self.file)
        lines = f.readlines()
        f.close()

        for line in lines:
            try:
                (user,password) = line.rstrip().split(self.delimiter,2)
                self.data[user] = password
            except ValueError:
                # got invalid line
                continue

    def has_key(self, key):
        return self.data.has_key(key)

    def _get(self, key):
        return self.data[key]

import hashlib
class Md5FileBackend(FileBackend):
    passwordStorage=MD5_HASH

    """
    File Backend where the passwords are stored as MD5 hash from username, realm and password
    """
    def passHash(self, username, password, realm):
        return hashlib.md5('%s:%s:%s' % (username, realm, password)).hexdigest();

from core.pattern import Decorator
import core.pool.Redis as Redis
class CacheDecorator(Decorator):
    connectionWrapper = None

    def __init__(self, obj, expiration=3600, prefix="auth_"):
        Decorator.__init__(self, obj)
        object.__setattr__(self, "connectionWrapper", None)
        object.__setattr__(self, "prefix", prefix)
        object.__setattr__(self, "expiration", expiration)

    def check(self, username, password, realm):
        key = hashlib.md5("%s-%s-%s" % (username, password, realm)).hexdigest()
        cacheKey = self.getCacheKey(key)
        redis = self._getClient()
        value = redis.get(cacheKey)
        if value:
            return True

        value = self._obj.check(username, password, realm)
        if value:
            redis.set(cacheKey, value)
            redis.expire(cacheKey, self.expiration)
        return value

    def has_key(self, key):
        cacheKey = self.getCacheKey(key)
        redis = self._getClient()
        value = redis.get(cacheKey)
        if value:
            return True

        value = self._obj._get(key)
        if value:
            redis.set(cacheKey, value)
            redis.expire(cacheKey, self.expiration)
        return value

    def get(self, key, defaultValue=None):
        try:
            return self._get(key)
        except KeyError:
            return defaultValue

    def __getitem__(self, key):
        if isinstance(key, slice):
            raise ValueError("The key cannot be slice")

        return self._get(key)

    def _get(self, key):
        cacheKey = self.getCacheKey(key)
        redis = self._getClient()
        value = redis.get(cacheKey)
        if value:
            return value
        
        value = self._obj._get(key)
        if value:
            redis.set(cacheKey, value)
            redis.expire(cacheKey, self.expiration)

        return value

    def delKey(self, key):
        redis.delete(self.getCacheKey(key))

    def getCacheKey(self, key):
        return self.prefix + key

    def _getClient(self):
        if not self.connectionWrapper:
            object.__setattr__(self, "connectionWrapper", Redis.ConnectionPool().get())
        return self.connectionWrapper.getConnection()

    def __del__(self):
        # delete object references manually
        if self.connectionWrapper is not None:
            object.__delattr__(self, 'connectionWrapper')
        Decorator.__del__(self)