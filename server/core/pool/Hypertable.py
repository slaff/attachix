"""
Hypertable Connection Pool
"""
from hypertable.thriftclient import ThriftClient

import base
class ConnectionPool(base.LocalConnectionPool):
    expiration = 0 # always recheck connections from the pool

    @classmethod
    def create(cls, *args, **settings):
        """
        Makes the real connection to the data source and returns it.

        @param string host
        @param int    port
        @param string namespace
        @return object
        """
        if not settings.has_key('host'):
            settings['host'] = 'localhost'
        if not settings.has_key('port'):
            settings['port'] = 38080
        if not settings.has_key('namespace'):
            settings['namespace'] = '/'
        
        client = ThriftClient(settings['host'], settings['port'])
        namespace = client.open_namespace(settings['namespace'])

        return [client,namespace]

    def _getSocket(self, client):
        return (client[0].transport._TFramedTransport__trans).handle

    def close(self, client):
        client[0].close()