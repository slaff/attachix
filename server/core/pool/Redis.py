"""
Redis Connection Pool
"""
import base
import logging

import redis
class ConnectionPool(base.LocalNullConnectionPool):

    @classmethod
    def create(cls, *args, **settings):
        """
        Makes the real connection to the data source and returns it.

        @param string host
        @param int    port
        @param int    db
        @return object
        """
        if not hasattr(cls._instance, 'pool'):
            logging.getLogger().debug('Pool: Redis - creating new redis pool')
            cls._instance.pool = redis.ConnectionPool(max_connections = cls._instance.maxSize, **settings)
        else:
            logging.getLogger().debug('Pool: Reusing internal redis pool: %s' % cls._instance.pool)

        client = redis.StrictRedis(**settings)
        return client

    def ping(self, client):
        try:
            client.ping()
        except:
            return False

        return True

