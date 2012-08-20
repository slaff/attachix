"""
RabbitMQ Connection Pool
"""
from amqplib import client_0_8 as amqp
import conf.server

import base
class ConnectionPool(base.LocalConnectionPool):
    expiration = 0 # always recheck connections from the pool

    @classmethod
    def create(cls, *args, **settings):
        """
        Makes the real connection to the data source and returns it.

        @param string server
        @param string user
        @param string password
        @param string vhost
        @return object
        """
        config = conf.server.Config['queue']
        connection = amqp.Connection(host="%s:%s" % (config['server'], config['port']),
                                     userid=config['user'],
                                     password=config['password'],
                                     virtual_host=config['vhost'],
                                     insist=False)
        return connection

    def _getSocket(self, client):
        return client.transport.sock

    def close(self, client):
        client.close()