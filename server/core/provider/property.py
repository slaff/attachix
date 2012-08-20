class Base():
    """
    Simple Property Provider that is actually nothing more then normal dictionary
    """
    def get(self, key, field=None):
        """
        Implement this method in the child class
        """
        return {}

    def set(self, key, field, value):
        """
        Implement this method in the child class
        """
        pass

    def delete(self, key, field=None):
        """
        Implement this method in the child class
        """
        pass

    def items():
        return []

    def has_key(self, key):
        return false

    def __getitem__(self, key):
        return {}

    def __delitem__(self, key):
        pass

from core.pool.Redis import ConnectionPool
class Redis():
    redis = None
    def __init__(self, prefix="props_"):
        # @todo: Move this to configuration file
        self.prefix = prefix
        self.redis = ConnectionPool().getConnection()

    def get(self, key, field=None):
        if field is None:
            return self.redis.hgetall(self.getCacheKey(key))
        else:
            return self.redis.hget(self.getCacheKey(key), field)

    def set(self, key, field, value):
        return self.redis.hset(self.getCacheKey(key),field, value)

    def delete(self, key, field=None):
        if field is None:
            return self.redis.delete(self.getCacheKey(key))
        else:
            return self.redis.hdel(self.getCacheKey(key), field)

    def items():
        return self.redis.hgetall(self.getCacheKey(key)).items()

    def has_key(self, key):
        return self.redis.exists(self.getCacheKey(key))

    def __getitem__(self, key):
        return self.redis.hgetall(self.getCacheKey(key))

    def __delitem__(self, key):
        return self.delete(self.getCacheKey(key))

    def getCacheKey(self, key):
        return "%s%s" % (self.prefix, key)