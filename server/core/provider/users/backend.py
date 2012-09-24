# [ User Backends ] #
class AbstractBackend():
    identity = None
    
    def find(self, identity):
        """
        Try to find user with the specified identity
        @return None on failure  or object instanceof AbstractBackend
        """
        raise Exception("Implement this method in the child class")

    def getIdentity(self):
        return self.identity

    def hasQuota(self, expectedSize):
        raise Exception("Implement this method in the child class")

    def changeQuota(self, bytes):
        """
        @param int bytes
        """
        raise Exception("Implement this method in the child class")

    def has_key(self, key):
        raise Exception("Implement this method in the child class")

    def get(self, key, defaultValue=None):
        try:
            return self._get(key)
        except ValueError:
            return defaultValue



    def __getitem__(self, key):
        if isinstance(key, slice):
            raise ValueError("The key cannot be slice")

        return self._get(key)

    def __setitem__(self, key, value):
        raise Exception("Implement this method in the child class")

    def _get(self, key):
        raise Exception("Implement this method in the child class")

    def inc(self, value):
        raise Exception("Implement this method in the child class")

    def save(self):
        raise Exception("Implement this method in the child class")

class DummyBackend(AbstractBackend):

    def find(self, identity):
        """
        Try to find user with the specified identity
        @return boolean True on success or False otherwise
        """
        self.identity = identity
        return self

    def has_key(self, key):
        return False

    def __getitem__(self, key):
        if isinstance(key, slice):
            raise ValueError("The key cannot be slice")

        return self._get(key)

    def __setitem__(self, key, value):
        return False

    def _get(self, key):
        if key=='id':
            return self.identity
        raise KeyError('No such key')

    def inc(self, value):
        return False

    def save(self):
        return False

    def hasQuota(self, expectedSize):
        return True

    def changeQuota(self, bytes):
        """
        @param int bytes
        """
        return False

    




    