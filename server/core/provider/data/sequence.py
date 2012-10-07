import core.pool.Redis as Redis
class Generator(object):
    """
    Generator for unique sequence numbers
    """
    def __new__(cls, prefix='sequence_', **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
            cls._instance.redis = Redis.ConnectionPool(**kwargs).getConnection()
            cls._instance.prefix = prefix

        return cls._instance
    
    def get(cls, name, fillChar=None, length=0):
        """
        Generates the next id for an item with name
        """
        sequence = cls.redis.incr(cls.getCacheKey(name))
        sequence = "%s" % sequence
        if fillChar is not None and length!=0:
            sequence = sequence.rjust(length, "%s" % fillChar)

        return sequence
    
    def reset(cls, name, startValue=0):
        """
        Resets a sequence value with with startValue
        """
        cls.redis.set(cls.getCacheKey(name), "%d" % startValue)

    def getCacheKey(cls, name):
        return cls.prefix +  name