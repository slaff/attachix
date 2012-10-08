import re

from gevent import Timeout
from core.models.event import Event

class Events():
    """
    Events Controller
    """
    
    auth = None

    def __init__(self, auth):
        self.auth = auth

    def get_Files(self, request):
        request.setResponseCode(200)
        request.setHeader('Content-Type', 'text/event-stream')
        request.setHeader('Expires', 'Fri, 01 Jan 1990 00:00:00 GMT')
        request.setHeader('Cache-Control', 'no-cache, no-store, max-age=0, must-revalidate')
        request.setHeader('Pragma','no-cache')
        request.setHeader('Access-Control-Allow-Origin', '*')
        
        retry = 1000 # retry time in miliseconds
        wait = 15
        if request.env.has_key('HTTP_X_SUBSCRIPTION_WAIT'):
            try:
                wait = int(request.env['HTTP_X_SUBSCRIPTION_WAIT'])
            except Exception:
                pass

        # @todo: Figure out if the connection should be closed or not
        close = True

        eventQueue = Event()
        userObject = self.getUser(request)
	if not userObject:
	    return

        lastId = None
        try:
            if request.env.has_key('HTTP_LAST_EVENT_ID'):
                lastId =  request.env['HTTP_LAST_EVENT_ID']
            elif request.params.has_key('Last-Event-ID'):
                lastId = request.params['Last-Event-ID']

            if lastId is not None:
                lastId = "%.4f" % lastId
        except Exception:
                pass

        channel = "%s.files" % userObject.get('id')
        events = eventQueue.subscribe(channel, lastId)
	timeout = None
        try:
            """
            @warninig: If the connection is closed from haproxy for some reason
                       this connection is not recycled. That's why we close the
                       connection after 15 seconds (the haproxy timeout is set
                       to 20 seconds).
            @todo:     Figure out why the closing on the other side is not detected
                       and the connection hangs
            @todo:     Figure out how to set a timeout that sends noop command
                       every 15 seconds and keeps the connection alive for ever.
            """
            if close:
                timeout = Timeout(wait).start()
            for event in events:
                if request.env.has_key('BASE_URI'):
                    event = re.sub(r'"resource":\s*"(.*?)"', '"resource": "%s\\1"' % request.env['BASE_URI'], event)

                if request.env.has_key('URI_REPLACE'):
                    match = re.search(r'"resource":\s*"(.*?)"', event)
                    if match:
                        uri = match.group(1).replace(request.env['URI_REPLACE'][0],request.env['URI_REPLACE'][1])
                        event = re.sub(r'"resource":\s*"(.*?)"', '"resource": "%s"' % uri, event)

                text  = ": %s\n" % ''.center(2049,' ') # 2kb padding for IE
                text += "data: {\"files\": %s}\n" % event
                match = re.search(r'"time":\s*([0-9.]+)',event)
                if match:
                    text += "id: %s\n\n" % match.group(1)
                yield text

                if not close:
                    continue

                # if we have to close then reset the timeout
                if timeout is not None:
                    timeout.clear()
                timeout = Timeout(wait).start()
                yield ":noop\n"
        except Timeout:
            yield "retry: %d" % retry
        finally:
            if hasattr(events, 'close') and callable(events.close):
                events.close()
	    if timeout is not None:
                timeout.cancel()

    get_All = get_Files

    post_All = get_Files
    
    def getUser(self, request):
        if request.env.has_key('user'):
            return request.env['user']

        if not self.auth.authenticate(request):
            return
        request.env['user'] = self.auth.getUser(request)
        return request.env['user']
