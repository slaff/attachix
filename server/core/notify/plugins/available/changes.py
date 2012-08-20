from core.models.event import Event
from core.notify.plugins import base
import core.utils as utils
import time
import urlparse

class Plugin(base.Plugin):
    subscribe = ['PUT', 'MKCOL','POST', 'PROPPATCH', 'COPY','MOVE', 'DELETE']

    name    = 'Changes Plugin'
    description = 'Plugin that reports changes of a file to the major job queue'
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
        Gets information about the event and reports it to the Redis pub/sub
        """
        key    = "%s.files" % user.get('id')
        event = Event()

        type = 'add'
        if request.method == 'DELETE':
            type = 'remove'

        uri = request.uri.replace(request.baseUri,'')

        if request.method == 'POST':
            commonString = utils.longestCommonSubstring(uri, path)
            uri += path.replace(commonString,'')
        elif request.method in ['COPY','MOVE']:
            uri = urlparse.urlparse(request.env['HTTP_DESTINATION'])[2]
            uri = uri.replace(request.baseUri,'')
            baseUri = request.uri.replace(request.baseUri,'').replace(path,'')
            if baseUri:
                path = uri.replace(baseUri,'/')
            else:
                path = uri

        meta = None
        if type!='remove':
            meta = resource.storageProvider.getMeta(path, user=user)
            meta = meta[path]

        timestamp = time.time()
        data = {
            'time': timestamp,
            'type': type,    # add|remove
            'resource': uri,
            'meta': meta
        }
        event.publish(key, data, timestamp)

        if request.method == 'MOVE':
            timestamp = time.time()
            data = {
                'time': timestamp,
                'type': 'remove',    # add|remove
                'resource': request.uri,
                'meta': None
            }

            event.publish(key, data, timestamp)
