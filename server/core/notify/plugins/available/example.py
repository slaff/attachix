import logging
from core.notify.plugins import base

class Plugin(base.Plugin):
    
    name    = 'Example Plugin'
    description = 'Just for demonstration purposes'
    author  = 'Slavey Karadzhov <slaff@linux-bg.org>'
    version = '0.1'

    """
    @param int user
    @param Request request
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
        logging.getLogger().debug("[Example Plugin]: \
                User: %s \
                Request: %s \
                Resource: %s,\
                Path: %s, \
                Meta: %s" % \
              (user, request, resource, path, meta)
        )
