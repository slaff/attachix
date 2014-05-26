# -*- coding: utf-8 -*-
import gevent
import magic
import ujson as json

mimeDB = magic.open(magic.MAGIC_MIME)
mimeDB.load()

def getMime(filename):
    """
    Returns the mime type and the encoding of a file
    """
    line = mimeDB.file(filename)
    if line is not None:
        parts = line.split(';')
        mime = parts[0].strip()
        if mime.find('/')==-1:
            mime = 'application/octet-stream'
        elif mime == 'text/html' and \
           (filename[-5:].lower() == '.xslt' or filename[-4:].lower() == '.xsl'):
            # @notice: workaround for the broken mime detection on debian
            # @todo: fix the real problem and remove this code
            mime = 'application/xml'
        encoding = None
        if len(parts)==2:
            encoding = parts[1][9:]
        return mime, encoding
    return None, None

from gevent.hub import get_hub
def async(func):
    def newFunction(*args, **kwargs):
        return get_hub().threadpool.apply(func, args, kwargs)

    return newFunction

from gevent import socket
import errno
import fcntl
import subprocess
import os
import sys
import logging
def popenCommunicate(args, data='', outputs=None, ignoreErrors=False,  poll_interval=0.01):
        """
        Communicate with the process non-blockingly.
        @param outputs list of file like objects
        """
        stdError = None
        if not ignoreErrors:
            stdError = subprocess.STDOUT
        p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stdError)
        fcntl.fcntl(p.stdin, fcntl.F_SETFL, os.O_NONBLOCK) # make the file nonblocking
        fcntl.fcntl(p.stdout, fcntl.F_SETFL, os.O_NONBLOCK) # make the file nonblocking

        bytesTotal = len(data)
        bytesWritten = 0
        while bytesWritten < bytesTotal:
            try:
                # p.stdin.write() doesn't return anything, so use os.write.
                bytesWritten += os.write(p.stdin.fileno(), data[bytesWritten:])
            except IOError, ex:
                if ex[0] != errno.EAGAIN:
                    raise
                sys.exc_clear()
            socket.wait_write(p.stdin.fileno())

        p.stdin.close()

        if outputs is not None:
            while True:
                try:
                    chunk = p.stdout.read(4096)                    
                    if not chunk:
                        break
                    for output in outputs:
                        output.write(chunk)
                except IOError, ex:
                    if ex[0] != errno.EAGAIN:
                        raise
                    sys.exc_clear()
                socket.wait_read(p.stdout.fileno())            

        p.stdout.close()

        length = None
        try:
            length = len(outputs[0])
        except:
            length = 0

        logging.getLogger().debug("popenCommunicate() finished. Args: %s, Output Length: %d" % (args,length))

class OrderedDict():
    """
    This class needs to take dictionary as an input and transform it
    to ordered dictionary, that can be sliced and that can be sorted.
    The lists returned by keys(), values() and items() are
    in the insertion order.
    """
    _sequence  = []
    dictionary = None

    def __init__(self, dictionary=None):
        if dictionary is not None:
            self.dictionary = dictionary
        else:
            self.dictionary = {}
        self._sequence = self.dictionary.keys()

    def get(self, keys):
        return self.dictionary.get(keys)

    def has_key(self, key):
        return self.dictionary.has_key(key)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.__getslice___(key.start, key.stop)
        
        if type(key) == int:
            key = self._sequence[key]        
        return self.dictionary[key]

    def __setitem__(self, key, item):
        self._sequence.append(key)
        self.dictionary[key] = item
    
    def __getslice___(self,start,end):
        keys = self._sequence[start:end]
        dict = OrderedDict({})
        for key in keys:
            dict[key] = self.dictionary[key]
        return dict

    def values(self):
        values=[]        
        for key in self._sequence:
            values.append(self.dictionary[key])
        return values

    def items(self):
        items=[]
        for key in self._sequence:
            items.append((key, self.dictionary[key]))
        return items

    def keys(self):
        """
        Returns direct reference to the keys in the dictionary
        """
        return self._sequence

    def __len__(self):
        return len(self.dictionary)

    def sort(self, field=None, asc=True, castFunction=None):
        """
        Sort the dictionary by its values
        """
        if field is None or field == '':
            # sort the keys
            self._sequence.sort()
            return

        def cast(value):
            if not castFunction:
                return value
            else:
                return castFunction(value)

        def innerCmp(a,b):
            order = 1
            if asc == False:
                order = -1
            return cmp(cast(self.dictionary[a][field]), cast(self.dictionary[b][field])) * order

        self._sequence.sort(innerCmp)

    def filter(self, dict):
        """
        Removes elements that for a given key do not have the given value
        @todo: fix this method
        """
        for (pos, hashKey) in enumerate(self._sequence):
            for (key, value) in dict.items():
                data = self.dictionary[hashKey]
                
                if not (data.has_key(key) and data[key].find(value) == 0):
                    del self.dictionary[hashKey]
                    self._sequence.pop(pos)

    def __repr__(self):
        return repr(dict(self.items()))

    def toJson(self):
        """
        Writes JSON representation of the ordered dictionary
        preserving the order of the keys
        """
        text = '{'
        if len(self._sequence):
            for key in self._sequence:
                text += '"%s":%s,' % (key,json.dumps(self.dictionary[key]))
            text = text[:-1]
        text += '}'

        return text

def require(path,className=None):
    """
    Loads dynamically python modules
    """
    (dirname, basename) = os.path.split(path)
    packageName = dirname.replace('/','.')
    moduleName = basename.rstrip('.py')

    logging.getLogger().debug("Loading: %s.%s[%s]" %(packageName,moduleName,className))

    mod = __import__(packageName+'.'+moduleName, globals(), locals(), [className])
    if className:
        return getattr(mod, className)

    return mod

from cStringIO import StringIO
def mediaInfo(fileName):
    output = StringIO()
    args = [
            'mediainfo',
            '-f ',
            fileName
    ]
    popenCommunicate(args, '', [output])
    output.seek(0)
    info = {}
    section = None
    while True:
        line = output.readline()
        if not line:
            break

        line = line.strip()
        if line == '':
            continue

        try:
            (key, value) = line.split(':',1)
        except ValueError:
            section = line
            info[section] = {}
            continue

        key = key.strip()
        value = value.strip()

        if info[section].has_key(key):
            continue
            
        info[section][key] = value

    logging.getLogger().debug("MediaInfo:[%s]" % info)
    return info

def longestCommonSubstring(S1, S2):
    M = [[0]*(1+len(S2)) for i in xrange(1+len(S1))]
    longest, x_longest = 0, 0
    for x in xrange(1,1+len(S1)):
        for y in xrange(1,1+len(S2)):
            if S1[x-1] == S2[y-1]:
                M[x][y] = M[x-1][y-1] + 1
                if M[x][y]>longest:
                    longest = M[x][y]
                    x_longest  = x
            else:
                M[x][y] = 0
    return S1[x_longest-longest: x_longest]

import ntpath, posixpath, macpath
def baseName(filename):
    for m in posixpath, ntpath, macpath:
        if m.sep in filename:
            return m.basename(filename)
    else:
        return filename

class StreamRange():
    def __init__(self, stream, ranges):
        self.stream = stream
        self.ranges = ranges
        if isinstance(stream, file):
            import mmap
            self.stream = mmap.mmap(stream.fileno(), 0, prot=mmap.PROT_READ)

    def __iter__(self):
        return self

    def next(self):
        try:
            (start, end) = self.ranges.pop(0)
        except IndexError:
            raise StopIteration

        return self.stream[start : end+1]

import hashlib
def getMD5(stream):
    md5Sum = hashlib.md5()
    blockSize = 2**20
    while True:
        data = stream.read(blockSize)
        if not data:
            break
        md5Sum.update(data)
        # @notice: possible non-blocking func will require one sleep with 0 seconds
        gevent.sleep(0.00)
    return md5Sum