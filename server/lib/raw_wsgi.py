from gevent.pywsgi import WSGIHandler as _WSGIHandler, WSGIServer as _WSGIServer

class WSGIHandler(_WSGIHandler):
    """
    WSGIHandler class that provides also the original raw URI
    @see: https://groups.google.com/forum/?fromgroups&hl=en#!topic/gevent/CY6s4PwFMq0
    """

    def get_environ(self):
        environ = _WSGIHandler.get_environ(self)
        environ['RAW_URI'] = self.path
        return environ

class WSGIServer(_WSGIServer):
    handler_class = WSGIHandler