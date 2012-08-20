import os.path
from core.notify.plugins import base

class Plugin(base.Plugin):
    subscribe = ['PUT','POST']
    
    name    = 'Work Property Plugin'
    description = """This plugin should be enabled only for special URLs.
    It sole purpose is to automate the setting of the special properties
    after a worker has submitted its job to the token server.
    """
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
        Set the special property after a worker has submitted its job
        """

        fileName = os.path.basename(path)
        (name, extension) = os.path.splittext(file)

        # save the property
        key = resource.storageProvider._translateUri(path)
        field = '{protected:}%s' % name
        resource.storageProvider.setMeta(key,{field : fileName })
