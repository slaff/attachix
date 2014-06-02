import time
import logging
import select
import gevent.queue as queue
from gevent.lock import RLock
        
class ConnectionWrapper(object):
    """ConnectionWrapper """
    def __init__(self,pool,connection):
        self.pool = pool
        self.connection = connection

    def getConnection(self):
        return self.connection

    def __getattr__(self, name):
        return getattr(self.connection, name)

    def __getitem__(self, name):
        return self.connection[name]

    def __del__(self):
        self.pool.release(self.connection)
        del self.pool
        del self.connection

class ConnectionPool(object):

    params = []
    """
    Some server have timeouts for their client connections
    therefore we will need to revalidate the connection after this expiration time.
    """
    expiration = 60 # time in seconds
    overflow   = 2 # hardLimit = maxSize * <the-value-of-overflow>

    """Connection Pool Shared Across Greenlets/Threads"""
    def __new__(cls, minSize=5, maxSize=20, timeout=10, *args, **kwargs):
        """
        @param minSize -- pool minimum size
        @param maxSize -- the maximum size of the pool
        @param timeout -- time to wait in order to get an element from the pool
        """

        """
        @todo:
            [+]Add Pool size (maxSize) and initial connections(minSize) to create(as init argument)
            Remove broken/closed connections from the pool.
            Slowly increase or decrease the pool to its max or min size based on the demand.
        """
        if not hasattr(cls,'_instance'):
            cls._instance = object.__new__(cls)
            cls._instance.createdConnections = 0
            cls._instance.queue = queue.Queue(maxSize)
            cls._instance.minSize = minSize
            cls._instance.maxSize = maxSize
            cls._instance.timeout = timeout
            cls._instance.params = [args,kwargs]
            cls._instance.lock = RLock()

            hardLimit = maxSize* cls.overflow
            for x in xrange(minSize):
                cls._instance.queue.put([time.time(), cls.create(*args,**kwargs) ] )
                cls._instance.createdConnections += 1
                logging.getLogger().debug('Pool: Created new connection. %s (in queue: %s, created: %s, maxSize: %s, hardMaxSize: %s)' % \
                                         (cls._instance.__class__, cls._instance.queue.qsize(), cls._instance.createdConnections, cls._instance.maxSize, hardLimit))
                

        return cls._instance

    @classmethod
    def create(cls, *args, **kwargs):
        """
        Makes the real connection to the data source and returns it.
        Notice: Implement the creation of the connection in the child class
        
        @return object
        """
        raise Exception('Not Implemented')

    def _getSocket(self, client):
        """
        Gets the transport socket from the client
        Notice: Implement this method in the child class

        @return socket
        """
        raise Exception('Implement in child class')

    def ping(self, client):
        """
        Checks if the connection is still alive.
        Override this method in the child class if needed

        @return boolean
        """
        sock = self._getSocket(client)
        if not sock:
            return False
        rlist,wlist,xlist = select.select([sock], [], [], 0)
        if rlist:
            # the socket is readable, meaning there is either data from a previous call
            # (i.e our protocol is out of sync), or the connection was shut down on the
            # remote side. Either way discard this connection
            return False
        return True

    def get(self):
        """
        Get connection from the pool
        """
        client = None
        logging.getLogger().debug('Pool: Size: %d, For: %s' % (self.queue.qsize(), self.__class__))
        try:
            block = self.createdConnections > self.maxSize
            (accessed, client) = self.queue.get(block, self.timeout)
        except queue.Empty:
            logging.getLogger().warn('Pool: No connection in pool: %s' % self.__class__)

        if client is not None and accessed + self.expiration < time.time() :
            # check if the client is still valid
            logging.getLogger().debug('Pool: Pinging client: %s' % client)
            if not self.ping(client):
                logging.getLogger().debug('Pool: Discarding Invalid Connection: %s' % client)
                try:
                    self.close(client)
                except Exception, ex:
                    logging.getLogger().warn('Pool: Unable to close client. Got exception: %s' % ex)
                client = None
                self.createdConnections -= 1

        if not client:
            if self.queue.qsize() > self.minSize:
                logging.getLogger().debug('Pool: Waiting for connection. %s (in queue: %s, created: %s, maxSize: %s)' % \
                                             (self.__class__, self.queue.qsize(), self.createdConnections, self.maxSize))
                return self.get()

            self.lock.acquire()
            try:
                hardLimit = self.maxSize*self.overflow
                if self.createdConnections < hardLimit:
                    logging.getLogger().debug('Created: %d, Hard Limit: %d' % (self.createdConnections, hardLimit))
                    client = self.create(*self.params[0], **self.params[1])
                    self.createdConnections += 1
                    logging.getLogger().debug('Pool: Created new connection. %s (in queue: %s, created: %s, maxSize: %s, hardMaxSize: %s)' % \
                                             (client, self.queue.qsize(), self.createdConnections, self.maxSize, hardLimit))
            finally:
                self.lock.release()


        if not client:
            logging.getLogger().debug('Pool: Waiting for connection. %s (in queue: %s, created: %s, maxSize: %s)' % \
                                             (self.__class__, self.queue.qsize(), self.createdConnections, self.maxSize))
            return self.get()
        
        return ConnectionWrapper(self, client)

    def getConnection(self):
        """Gets the object connection to the data source"""
        return self.get().getConnection()

    def close(self, client):
        """
        Closes the connection to the client
        Notice: Implement this method in the child class
        """
        return False

    def release(self, client):
        """
        Returns connection back to the pool
        """
        try:
            self.queue.put([time.time(), client], False)
            logging.getLogger().debug('Pool: Connection returned: %s' % client)
        except queue.Full:
            try:
                self.close(client)
            except Exception, ex:
                logging.getLogger().warn('Pool: Unable to close client. Got exception: %s' % ex)
            self.createdConnections -= 1
            logging.getLogger().warn('Pool: Pool is full. Size: %d(Created: %d)' % (self.queue.qsize(), self.createdConnections))

    def __repr__(self):
        return "Size: %d [%s:%s], Created: %d, Lost: %d" % (self.queue.qsize(), self.minSize, self.maxSize, self.createdConnections, (self.createdConnections - self.queue.qsize()))

from threading import local
class LocalConnectionPool(ConnectionPool):
    timeout = 120 # seconds

    """Connection Pool With only one connection per thread/greenlet"""
    def __new__(cls, minSize=5, maxSize=20, timeout=30, *args, **kwargs):
        """
        @param size -- pool size
        @param *args
        @param **kwargs
        """
        if not hasattr(cls,'_instance'):
            cls._instance = ConnectionPool.__new__(cls, minSize=5, maxSize=20, timeout=30, *args, **kwargs)
            cls._instance.local = local()

        return cls._instance

    def get(self):
        """Gets the object with the connection to the data source"""

        if hasattr(self.local, 'accessed') and self.local.accessed < time.time() - self.timeout:
            # hm - the same thread but not accessed recently
            try:
                logging.getLogger().debug('Deleting stale connection from the thread')
                del self.local.connection
            except:
                pass

        if not hasattr(self.local,'connection'):
            logging.getLogger().debug('Pool: New ThreadLocal Connection: %s' % self.__class__)
            self.local.connection = ConnectionPool.get(self)
        else:
            logging.getLogger().debug('Pool: Reusing Connection %s (%s)' % (self.local.connection, self.__class__))
        self.local.accessed = time.time()
        return self.local.connection

class NullConnectionPool(object):
    """
    Makes a connection every time the get method is called
    """

    timeout = 120 # seconds

    def __new__(cls, minSize=5, maxSize=20, timeout=30, *args, **kwargs):
        """
        @param size -- pool size
        @param *args
        @param **kwargs
        """
        if not hasattr(cls,'_instance'):
            cls._instance = object.__new__(cls)
            cls._instance.minSize = minSize
            cls._instance.maxSize = maxSize
            cls._instance.params = [args,kwargs]

        return cls._instance

    @classmethod
    def create(cls, *args, **kwargs):
        """
        Makes the real connection to the data source and returns it.
        Notice: Implement the creation of the connection in the child class

        @return object
        """
        return None

    def get(self):
        """Gets the object with the connection to the data source"""
        logging.getLogger().debug('Pool: Creating new client for: %s' % self.__class__)
        return ConnectionWrapper(self, self.create(*self.params[0],**self.params[1]))

    getConnection = get

    def release(self, client):
        try:
            self.close(client)
        except Exception, ex:
            logging.getLogger().warn('Pool: Unable to close client. Got exception: %s' % ex)

    def close(self, client):
        """
        Closes the connection to the client
        Notice: Implement this method in the child class
        """
        return False

class LocalNullConnectionPool(NullConnectionPool):
    """
    Makes a connection every new thread
    """

    timeout = 120 # seconds

    def __new__(cls, minSize=5, maxSize=20, timeout=30, *args, **kwargs):
        """
        @param size -- pool size
        @param *args
        @param **kwargs
        """
        if not hasattr(cls,'_instance'):
            cls._instance = NullConnectionPool.__new__(cls, minSize, maxSize, timeout, *args, **kwargs)
            cls._instance.local = local()

        return cls._instance

    def get(self):
        """Gets the object with the connection to the data source"""

        if hasattr(self.local, 'accessed') and self.local.accessed < time.time() - self.timeout:
            # hm - the same thread but not accessed recently
            try:
                logging.getLogger().debug('Pool: Deleting stale connection from the thread %s' % self.__class__)
                del self.local.connection
            except:
                pass

        if not hasattr(self.local,'connection'):
            logging.getLogger().debug('Pool: New ThreadLocal Connection %s' % self.__class__)
            self.local.connection = NullConnectionPool.get(self)
        else:
            logging.getLogger().debug('Pool: Reusing Connection %s' % self.local.connection)
            
        self.local.accessed = time.time()
        return self.local.connection

    getConnection = get