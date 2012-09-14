class Factory():
    """
    Factory class that allows you to use multiple user backends
    based on the user identifier
    """
    
    def __init__(self, rules):
        """
        @param rules resourceTree
        """
        self.rules = rules

    def find(self, identity):
        """
        Finds a user by its identity,
        @param string identity string[email]
        @returns None if none is found or
                 a new object based on the backend
        """
        
        parts = identity.split('.')
        uri = '/'.join(parts.reverse())

        # Based on the rules and the identity decide which backend to use.
        #       For example: x@gmail.com -> can try to get the data about the
        #       user from the gmail API
        backend = Resolver.getResourcePathForUri(uri, self.rules)
        if backend is None:
            return None
        return backend.find(identity)