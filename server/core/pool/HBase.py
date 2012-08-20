"""
HBase Connection Pool
"""
import base

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# HBase thrift driver
from hbase import Hbase
from hbase.ttypes import *

class ConnectionPool(base.LocalConnectionPool):
    @classmethod
    def create(cls, *args, **settings):
        """
        Makes the real connection to the data source and returns it.

        @param string host
        @param int    port
        @return object
        """
        # Make socket
        if not settings.has_key('host'):
            settings['host'] = 'localhost'
        if not settings.has_key('port'):
            settings['port'] = 9090
        transport = TSocket.TSocket(settings['host'], settings['port'])
        # Buffering is critical. Raw sockets are very slow
        transport = TTransport.TBufferedTransport(transport)
        # Wrap in a protocol
        protocol = TBinaryProtocol.TBinaryProtocol(transport)

        client = Hbase.Client(protocol)
        transport.open()
        return client