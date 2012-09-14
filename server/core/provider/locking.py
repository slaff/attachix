import logging
import time

DEFAULT_TIMEOUT = 3600

SCOPE_EXCLUSIVE = 1
SCOPE_SHARED    = 0

TYPE_READ       = 0
TYPE_WRITE      = 1

class LockProvider():

    def getLocks(self, uri, **kwargs):
        """
        Returns lock tokens
        {
            'token': {
                    'expiration',
                    'owner',
                    'type',
                    'scope'
            }
        }

        """
        pass

    def getSupportedLocks(self, uri, **kwargs):
        """
        Returns list with tuples of supported locks
        return [(scope, type)]
        """
        pass

    def lock(self, uri, timeout, owner, type, scope, **kwargs):
        """
        Returns lock token
        """
        pass

    def unlock(self, uri, token, **kwargs):
        """
        Unlocks uri with the given token
        Throws an exception if the URI cannot be unlocked with the given token
        """
        pass

    def refresh(self, uri, token, timeout, **kwargs):
        """
        Refreshes given token
        """
        pass



from copy import deepcopy
import uuid
class MemoryLockProvider(LockProvider):

    storage = {}

    """
    Class that keeps all the tokens in memory
    Useful for testing purposes and not quite useful in real life
    because it can be exploited by creating millions of locks in memory,
    plus it can be accessed only from the local server
    """
    def getLocks(self, uri, **kwargs):
        """
        Returns lock tokens
        {
            'token': {
                    'expiration',
                    'owner',
                    'type',
                    'scope'
            }
        }

        """
        if not MemoryLockProvider.storage.has_key(uri):
            return None

        now = time.time()
        for (token, data) in MemoryLockProvider.storage[uri].items():
            if data['expiration'] < now:                
                del MemoryLockProvider.storage[uri][token]

        return deepcopy(MemoryLockProvider.storage[uri])

    def getSupportedLocks(self, uri, **kwargs):
        """
        Returns list with tuples of supported locks
        """
        return [('exclusive', 'write')]


    def lock(self, uri, timeout, owner, type, scope, **kwargs):
        """
        Returns lock token
        """
        token = "%s" % uuid.uuid1()

        if not timeout:
            timeout = DEFAULT_TIMEOUT
        else:
            timeout = int(timeout)

        if not MemoryLockProvider.storage.has_key(uri):
            MemoryLockProvider.storage[uri] = {}
            
        MemoryLockProvider.storage[uri][token] = {
            'expiration': time.time()+timeout,
            'owner': owner,
            'type' : type,
            'scope': scope
        }

        return token

    def unlock(self, uri, token, **kwargs):
        """
        Unlocks uri with the given token
        Throws an exception if the URI cannot be unlocked with the given token
        """
        del MemoryLockProvider.storage[uri][token]

    def refresh(self, uri, token, timeout, **kwargs):
        """
        Refreshes given token
        Throws an error if there is no such token to refresh
        """

        MemoryLockProvider.storage[uri][token]['expiration'] = time.time()+timeout

import core.pool.Redis as Redis
import ujson as json
class RedisLockProvider(LockProvider):
    def __init__(self, host='localhost', port=6379, db=0, keyPrefix="lock_"):
        logging.getLogger().debug("Connect To the Redis Connection Pool")
        self.redis = Redis.ConnectionPool(host=host, port=port, db=db).getConnection()
        self.keyPrefix = keyPrefix

    def getLocks(self, uri, **kwargs):
        """
        Returns lock tokens
        {
            'token': {
                    'expiration',
                    'owner',
                    'type',
                    'scope'
            }
        }

        """
        data = self.redis.get(self.getCacheKey(uri, **kwargs))
        if not data:
            return None

        try:
            data = json.loads(data)
        except:
            return None

        return {
            data[0]: {
                'expiration':  data[1],
                'owner': data[2],
                'type' : data[3],
                'scope': data[4]
            }
        }

    def getSupportedLocks(self, uri, **kwargs):
        """
        Returns list with tuples of supported locks
        """
        return [('exclusive')]

    def lock(self, uri, timeout, owner, type, scope, **kwargs):
        """
        Returns lock token
        """
        token = "%s" % uuid.uuid1()

        if not timeout:
            timeout = DEFAULT_TIMEOUT
        else:
            timeout = int(timeout)

        key = self.getCacheKey(uri, **kwargs)
        if not self.redis.setnx(key, json.dumps([token, time.time()+timeout, owner, type, scope])):
            raise ValueError('This URL is already locked')

        self.redis.expire(key, timeout)

        return token

    def unlock(self, uri, token, **kwargs):
        """
        Unlocks uri with the given token
        Throws an exception if the URI cannot be unlocked with the given token
        """
        key = self.getCacheKey(uri, **kwargs)
        data = self.redis.get(key)
        if not data:
            return

        try:
            bits = json.loads(data)
        except:
            self.redis.delete(key)
            return

        if bits[0] != token:
            raise KeyError('The provided token is not correct.')

        self.redis.delete(key)

    def refresh(self, uri, token, timeout, **kwargs):
        """
        Refreshes given token
        """
        key = self.getCacheKey(uri, **kwargs)
        data = self.redis.get(key)
        if not data:
            return False

        try:
            data = json.loads(data)
        except:
            self.redis.delete(key)
            return False

        if data[0] == token:
            logging.getLogger().warn('RedisLockProvider.refresh() Invalid lock data was stored.')
            return False

        self.redis.set(uri, json.dumps([token, time.time()+timeout, data[1], data[2], data[3]]))
        self.redis.expire(key, timeout)

    def getCacheKey(self, uri, **kwargs):
        return "%s%s%s" % (self.keyPrefix, kwargs.get('user').getIdentity(), uri)
