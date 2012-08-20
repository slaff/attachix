class Entity():
    backend = None
    __data = None

    def __init__(self, identity, backend):
        self.backedn = backend
        self.__data = backend.find(identity)
        if self.__data is None:
            raise Exception('Unknown identity')

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
        return self.__data[key]

    def inc(self, key, value):
        raise Exception("Implement this method in the child class")

    def save(self):
        raise Exception("Implement this method in the child class")

    def getIdentity(self):
        return self.backend.row

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


    
class UserFactory():
    """
    Wrapper Class around the actual user model.
    Use this class to read and modify properties of already existing user.
    """

    def __init__(self, backend):
        self.backend = backend

    def find(self, identity):
        """
        Finds a user by its identity,
        @returns None if none is found or
                 a new object based on the backend
        """
        return self.backend.get(identity, None)