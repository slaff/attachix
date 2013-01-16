# -*- coding: utf-8 -*-
"""
HTTP Request Class
"""
import logging
import calendar
from multipart import parse_form_data
import re
import string
from urllib import unquote
import urlparse

responseCodes = {
    200: 'OK',
    201: 'Created',
    204: 'No Content',
    206: 'Partial Content',
    207: 'Multi-Status',
    302: 'Found',
    304: 'Not Modified',
    400: 'Bad Request',
    401: 'Authorization Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    409: 'Conflict',
    412: 'Precondition Failed',
    415: 'Unsupported Media Type',
    423: 'Locked',
    424: 'Failed Dependancy',
    502: 'Bad Gateway',
    507: 'Insufficient Storage'
}

# datetime parsing and formatting
weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
monthname = [None,
             'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
weekdayname_lower = [name.lower() for name in weekdayname]
monthname_lower = [name and name.lower() for name in monthname]

MAX_MEMORY_CACHE = 400*1024

def fixEncoding(uri):
    guessList = ['utf8','latin1']
    for encoding in guessList:
        try:
            return uri.decode(encoding).encode('utf8')
        except:
            pass
    raise UnicodeDecodeError('Unable to guess encoding')

def normalizeUri(uri):
    uriUnquoted = unquote(uri)
    if uriUnquoted !=uri:
        # some webdav clients encode the url using latin1
        uri = fixEncoding(uriUnquoted)
    uri = re.sub(r'/\.{2,}', '/', uri)
    uri = re.sub(r'/{2,}', '/', uri)
    if uri[-1:] == '/' and len(uri) > 1:
        uri = uri[:-1]
    return uri

def parseForm(request):
    return  parse_form_data(request.env)

def parseRangeHeader(headerValue):
        """
        Parse the value of a Range header into (start, stop) pairs.

        In a given pair, either of start or stop can be None, signifying that
        no value was provided, but not both.

        @return: A list C{[(start, stop)]} of pairs of length at least one.

        @raise ValueError: if the header is syntactically invalid or if the
            Bytes-Unit is anything other than 'bytes'.
        """
        kind, value = headerValue.split('=', 1)
        kind = kind.strip()
        if kind != 'bytes':
            raise ValueError("Unsupported Bytes-Unit: %r" % (kind, ))
        unparsedRanges = filter(None, map(str.strip, value.split(',')))
        parsedRanges = []
        for byteRange in unparsedRanges:
            try:
                start, end = byteRange.split('-', 1)
            except ValueError:
                raise ValueError("Invalid Byte-Range: %r" % (byteRange, ))
            if start:
                try:
                    start = int(start)
                except ValueError:
                    raise ValueError("Invalid Byte-Range: %r" % (byteRange, ))
            else:
                start = None
            if end:
                try:
                    end = int(end)
                except ValueError:
                    raise ValueError("Invalid Byte-Range: %r" % (byteRange, ))
            else:
                end = None
            if start is not None:
                if end is not None and start > end:
                    # Start must be less than or equal to end or it is invalid.
                    raise ValueError("Invalid Byte-Range: %r" % (byteRange, ))
            elif end is None:
                # One or both of start and end must be specified.  Omitting
                # both is invalid.
                raise ValueError("Invalid Byte-Range: %r" % (byteRange, ))
            parsedRanges.append((start, end))
        return parsedRanges

"""
Get the response type based on the headers or the URI params

@param request
@return string
    - json
    - xml

"""
def getResponseType(request):
        responseType = 'xml'

        params = {}
        if request.query.strip() != '':
            try:
                params = dict(urlparse.parse_qsl(request.query))
            except:
                # ignoring the wrong query parameter
                pass

        if params.get('rt','').lower() == 'json':
            responseType = 'json'
        elif request.env.has_key('HTTP_ACCEPT') and \
        request.env['HTTP_ACCEPT'].find('application/json') > 0 and \
        request.env['HTTP_ACCEPT'].find('text/xml') == -1:
            responseType = 'json'
        elif (request.env.get('HTTP_X_RESPONSE_TYPE') and \
        request.env.get('HTTP_X_RESPONSE_TYPE').lower() == 'json'):
            responseType = 'json'
        elif (request.env.get('HTTP_X_REQUESTED_WITH') and \
        request.env['HTTP_X_REQUESTED_WITH'].lower() == 'xmlhttprequest'):
            responseType = 'json'
            
        return responseType

def timegm(year, month, day, hour, minute, second):
    """
    Convert time tuple in GMT to seconds since epoch, GMT
    """
    EPOCH = 1970
    if year < EPOCH:
        raise ValueError("Years prior to %d not supported" % (EPOCH,))
    assert 1 <= month <= 12
    days = 365*(year-EPOCH) + calendar.leapdays(EPOCH, year)
    for i in range(1, month):
        days = days + calendar.mdays[i]
    if month > 2 and calendar.isleap(year):
        days = days + 1
    days = days + day - 1
    hours = days*24 + hour
    minutes = hours*60 + minute
    seconds = minutes*60 + second
    return seconds

def stringToDatetime(dateString):
    """
    Convert an HTTP date string (one of three formats) to seconds since epoch.
    @copyright: The Twisted Matrix team
    @license: MIT
    """
    parts = dateString.split()

    if not parts[0][0:3].lower() in weekdayname_lower:
        # Weekday is stupid. Might have been omitted.
        try:
            return stringToDatetime("Sun, "+dateString)
        except ValueError:
            # Guess not.
            pass

    partlen = len(parts)
    if (partlen == 5 or partlen == 6) and parts[1].isdigit():
        # 1st date format: Sun, 06 Nov 1994 08:49:37 GMT
        # (Note: "GMT" is literal, not a variable timezone)
        # (also handles without "GMT")
        # This is the normal format
        day = parts[1]
        month = parts[2]
        year = parts[3]
        time = parts[4]
    elif (partlen == 3 or partlen == 4) and parts[1].find('-') != -1:
        # 2nd date format: Sunday, 06-Nov-94 08:49:37 GMT
        # (Note: "GMT" is literal, not a variable timezone)
        # (also handles without without "GMT")
        # Two digit year, yucko.
        day, month, year = parts[1].split('-')
        time = parts[2]
        year=int(year)
        if year < 69:
            year = year + 2000
        elif year < 100:
            year = year + 1900
    elif len(parts) == 5:
        # 3rd date format: Sun Nov  6 08:49:37 1994
        # ANSI C asctime() format.
        day = parts[2]
        month = parts[1]
        year = parts[4]
        time = parts[3]
    else:
        raise ValueError("Unknown datetime format %r" % dateString)

    day = int(day)
    try:
        month = int(monthname_lower.index(month.lower()))
    except ValueError:
        # Chrome submits the month as integer
        month = int(month)

    year = int(year)
    hour, min, sec = map(int, time.split(':'))
    return int(timegm(year, month, day, hour, min, sec))


def fixMimeType(fileName, mimeType):
    if fileName[-4:] == '.css' and mimeType[0:5] == 'text/':
        mimeType = 'text/css'

    return mimeType

class BaseRequest(object):
    uri = ''
    query = ''
    _state         = 0
    _responseCode  = 200
    _responseBody  = []
    _responseHeaders = []
    env            = {}
    __inputStream  = None

    def __init__(self, uri, env={}):
        self.env    = env
        self.method = 'GET'
        if env.has_key('REQUEST_METHOD'):
            self.method = env['REQUEST_METHOD']
        self.__inputStream = None
        if env.has_key('wsgi.input'):
            self.__inputStream = env['wsgi.input']
        self.uri    = uri
        self.query  = ''
        if '?' in self.uri:
            (self.uri, self.query) = self.uri.split('?', 1)
        self.uri = normalizeUri(self.uri)
        self.prepath = []
        self.postpath = string.split(self.uri[1:], '/')
        self.reset()

    def getState(self):
        """
        Gets the request state.
        0 - nothing done, 1-headers sent, 2-sending body, 3 - finished
        """
        return self._state

    def read(self, bytes):
        """
        Method that helps to use the BaseRequest class in
        a file-like manner.
        """
        return self.__inputStream.read(bytes)

    def readline(self):
        """
        Method that helps to use the BaseRequest class in
        a file-like manner.
        Notice: Implement it in the child class
        """
        return self.__inputStream.readline()

    def write(self, data):
        """
        Method that helps to use the BaseRequest class in
        a file-like manner.
        Notice: Implement it in the child class
        """
        pass

    def writeDirect(self, data, code=None, message=None):
        self._responseBody = data
        self._responseCode = code

    def close(self):
        """
        Dummy method that helps to use the BaseRequest class
        in file-like manner
        """
        pass

    def setResponseCode(self, code):
        self._responseCode = code

    def getResponseBody(self):
        if self._responseBody is None:
            return []
        else:
            return self._responseBody

    def setHeader(self, name, value):
        """
        Notice: Implement it in the child class
        """
        self._responseHeaders.append((name, value))

    def reset(self):
        """
        Method that resets the response code, headers, body and state
        """
        self._state = 0
        self._responseCode = 200
        self._responseHeaders = []
        self._responseBody = []