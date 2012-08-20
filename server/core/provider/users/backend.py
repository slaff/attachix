# [ User Backends ] #
class AbstractBackend():
    identity = None
    currentData = {}

    def load(self):
        pass

    def get(self, identity, defaultValue):
        obj = self()


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

    def _get(self, key):
        raise Exception("Implement this method in the child class")

    def inc(self, value):
        raise Exception("Implement this method in the child class")

    def save(self):
        raise Exception("Implement this method in the child class")

    def getIdentity(self):
        return self.backend.row
    
    def __getitem__(self, key):
        return self.backend[key]

    def has_key(self, key):
        return self.backend.has_key(key)

    def __setitem__(self, key, value):
        if key == 'id':
            raise KeyError('Changing the id of the user is not allowed')
        self.backend[key] = value

    def hasQuota(self, expectedSize):
        return self.backend['quota_available'] >= expectedSize

    def changeQuota(self, bytes):
        """
        @param int bytes
        """
        self.backend.inc('quota_available', bytes)

    