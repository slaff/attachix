class Plugin():

    subscribe = []
    """
    Subscribe for any of the supported HTTP methods
    'PUT','GET', 'POST', etc. [] is for all events
    """
    
    mime  = []
    """
    [] - handles all mime types, otherwise enter the beginning
    of the mime that will be handled - like: [audio/mp], [video/]
    this will handle all files with mime starting with audio/mp and
    video/
    """

    name    = '<Name>'
    description = '<Description>'
    author  = '<Author>'
    version = '<Version>'

    def canProcess(self, event, meta):
        """
        Checks if the plugin can process the given event for the given node
        @return boolean
        """
        if len(self.subscribe) and event not in self.subscribe:
            return False

        if len(self.mime) and meta.has_key('getcontenttype'):
            nodeMime = meta['getcontenttype']
            for mime in self.mime:
               if nodeMime.startswith(mime):
                    return True
            return False

        return True
    
    """
    @param int user
    @param Resource resource
    @param string event
    @param string uri  - the path in the global resource tree
    @param string path - the local resource path
    @param array meta
    """
    def process(self, user, request, resource, path, meta):
        """
        Implement this method in the child class
        """
        raise ValueError('Not implemented')

