from core.notify.plugins import base
import logging

class Plugin(base.Plugin):
    subscribe = ['DELETE']

    name    = 'Cleanup Plugin'
    description = 'Cleans the information after deleting an element'
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
        # Delete here all the views after deleting a resource
        pass
