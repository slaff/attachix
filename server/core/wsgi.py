import http
import logging
from urllib import quote

class Request(http.BaseRequest):
    __inputStream = None
    __outputHeaders = {} # easy to search output headers
    __responseCallback = None
    __form  = None
    __files = None
    env = {}

    __write = None # the internal write method

    CHUNK_SIZE = 2 ** 14

    def __init__(self, env, responseCallback, cache=None):
        if cache is None:
            cache = {}
        self.version = env['SERVER_PROTOCOL']
        self.method  = env['REQUEST_METHOD']
        self.rawUri = quote(env['PATH_INFO'])
        if env['QUERY_STRING']:
            self.rawUri +="?%s" % env['QUERY_STRING']
        http.BaseRequest.__init__(self, self.rawUri, env)
        self.query   = env['QUERY_STRING']
        self.__inputStream = env['wsgi.input']
        self.__responseCallback = responseCallback
        self.__write = None
        self.__form  = None
        self.__files = None

        self.env = env
        self.env['cache'] = cache # per-request data cache

        # debug data
        logging.getLogger().debug("Method: [%s], URI: [%s], Query: [%s]" %
                                           (self.method, self.uri,self.query))

    def setHeader(self, name, value):
        name = name.title()
        self._responseHeaders.append( (name, value) )
        if not self.__outputHeaders.has_key(name):
            self.__outputHeaders[name]=[]
        self.__outputHeaders[name].append(value)

    def read(self, bytes):
        return self.__inputStream.read(bytes)

    def readline(self):
        return self.__inputStream.readline()

    def writeResponse(self, code=None):
        if not code:
            code = self._responseCode
        self.__write = self.__responseCallback('%s %s' % (code, http.responseCodes[code]),self._responseHeaders)
        self._state = 2

    def writeDirect(self, data, code=None, message=None):
        self._responseCode = code
        self.write(data)
        self._state = 3

    def write(self, data):
        if self._state < 2:
            if hasattr(data,'len') and callable(data,'len'):
                self.setHeader('Content-Length',"%s" % len(data))

            self.writeResponse(self._responseCode)

        self._responseBody = data

    def finish(self):
        if self._state == 3:
            # request already finished
            return

        if self._state == 0:
            self.writeDirect('', self._responseCode)
            self._state = 1
            return

        self._state = 3

    def __processData(self):
        try:
           (self.__form, self.__files) = http.parseForm(self)
        except Exception as e:
           import traceback
           logging.getLogger().warn("Got form parse error: %s.\n%s" % (e, traceback.format_exc()))
           (self.__form, self.__files) = ({},{})

    @property
    def params(self):
        if self.__form is None:
            self.__processData()
        return self.__form

    @property
    def files(self):
        if self.__files is None:
            self.__processData()
        return self.__files

