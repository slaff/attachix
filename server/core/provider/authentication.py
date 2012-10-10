"""
Authentication classes
"""
from authentications.backend import MD5_HASH, CLEAR_TEXT, OTHER

import logging

from core.provider.authentications.backend import AbstractBackend
class AuthProvider():
    request  = None
    identity = None
    backend  = None

    def __init__(self, backend=None, userProvider=None):
        self.backend = backend
        self.userProvider = userProvider
        if isinstance(backend, AbstractBackend):
            self.backend.load()

    def hasData(self, request):
        """
        Checks if the identity and the credentials are provided
        @return boolean
        """
        return True

    def authenticate(self, request):
        if self._doAuthenticate(request):
            return True
        else:
            (code, headers, body) = self.getErrorResponse(request)
            for (name, value) in headers.items():
                request.setHeader(name, value)
            request.writeDirect(body, code)
            return False

    def setIdentity(self, request, identity):
        request.env['__IDENTITY__'] = identity

    def getIdentity(self, request):
        """
        Returns the identiy of the user
        """
        return request.env.get('__IDENTITY__')

    def getUser(self, request):
        identity = self.getIdentity(request)
        if self.userProvider is None:
            return None
        return self.userProvider.find(identity)

    def getErrorResponse(self, request):
        """
        Gets the error response code, headers and body.
        """
        headers = {'Content-Type': 'text/html'}

        body = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
 "http://www.w3.org/TR/1999/REC-html401-19991224/loose.dtd">
<HTML>
  <HEAD>
    <TITLE>Error</TITLE>
    <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=ISO-8859-1">
  </HEAD>
  <BODY><H1>401 Unauthorized.</H1></BODY>
</HTML>"""
        return [ 401, headers, body]

    def _doAuthenticate(self, request):
        """
        The actual authentication method.
        Implement this in the classes that inherit from this one.
        """
        pass

import os
class RemoteEnvAuthProvider(AuthProvider):
    def hasData(self, request):
        """
        Checks if the identity and the credentials are provided
        @return boolean
        """
        return os.environ.has_key('REMOTE_USER')

    def _doAuthenticate(self, request):
        if os.environ.has_key('REMOTE_USER'):
            self.setIdentity(request, os.environ['REMOTE_USER'])
            return True
        else:
            return False

import base64
import hashlib
import re
class BasicAuthProvider(AuthProvider):
    realm = ''
    users  = {}

    def __init__(self, realm, backend, **kwargs):
        self.realm = realm
        AuthProvider.__init__(self, backend, **kwargs)

    def hasData(self, request):
        """
        Checks if the identity and the credentials are provided
        @return boolean
        """
        try:
            m = re.match('^\s*Basic (.*?)$', request.env['HTTP_AUTHORIZATION'])
            if m:
                return True
        except:
            pass

        return False

    def _doAuthenticate(self, request):
        if not request.env.get('HTTP_AUTHORIZATION'):
            return False

        m = re.match('^\s*Basic (.*?)$',request.env['HTTP_AUTHORIZATION'])
        if m:
            try:
                code = m.group(1).rstrip()
                string = base64.b64decode(code)
                (username, password) = string.split(':',2)
            except ValueError, e:
                # incorrect header value
                return False

            if self.backend.check(username, password, self.realm):
                self.setIdentity(request, username)
                return True

        return False

    def getErrorResponse(self, request):
        ( code, headers,  body) = AuthProvider.getErrorResponse(self, request)
        headers['WWW-Authenticate'] = 'Basic realm="%s"' % self.realm

        return [code, headers,  body]


import time
import urllib2
class DigestAuthProvider(AuthProvider):
    code = 401

    def __init__(self, realm, backend, **kwargs):
        """Incomplete Python implementation of Digest Authentication.

        For the full specification. http://www.faqs.org/rfcs/rfc2617.html

        realm = AuthName in httpd.conf
        users = a dict of users containing {username:password}
        Solution URL: http://code.activestate.com/recipes/302378-digest-authentication/

        """
        if backend.passwordStorage not in [CLEAR_TEXT,MD5_HASH]:
            raise Exception('The backend must implement clear text or md5 hash storage')

        AuthProvider.__init__(self, backend, **kwargs)
        self.realm = realm

    def hasData(self, request):
        """
        Checks if the identity and the credentials are provided
        @return boolean
        """
        try:
            m = re.match('^\s*Digest (.*?)$',request.env['HTTP_AUTHORIZATION'])
            if m:
                return True
        except:
            pass

        return False

    def H(self, data):
        return hashlib.md5(data).hexdigest()

    def KD(self, secret, data):
        return self.H(secret + ":" + data)

    def A1(self, request):
        # If the "algorithm" directive's value is "MD5" or is
        # unspecified, then A1 is:
        # A1 = unq(username-value) ":" unq(realm-value) ":" passwd
        username = request.env['__DIGEST_PARAMS__']["username"]
        passwd = self._getPassword(request, username)
        return "%s:%s:%s" % (username, self.realm, passwd)
        # This is A1 if qop is set
        # A1 = H( unq(username-value) ":" unq(realm-value) ":" passwd )
        #         ":" unq(nonce-value) ":" unq(cnonce-value)

    def _getPassword(self, request, username):
        if not request.env['__DIGEST_PARAMS__'].has_key('password'):
            request.env['__DIGEST_PARAMS__']['password'] = self.backend.get(username, "")

        return request.env['__DIGEST_PARAMS__']['password']


    def _checksum(self, request):
        username = request.env['__DIGEST_PARAMS__']["username"]
        return  self._getPassword(request, username)

    def A2(self, request):
        # If the "qop" directive's value is "auth" or is unspecified, then A2 is:
        # A2 = Method ":" digest-uri-value
        return request.method + ":" + request.rawUri
        # Not implemented
        # If the "qop" value is "auth-int", then A2 is:
        # A2 = Method ":" digest-uri-value ":" H(entity-body)

    def rspauth(self, request):
        if request.env['__DIGEST_PARAMS__'].get("qop","").lower() == "auth":
            # Check? and request.env['__DIGEST_PARAMS__']["qop"].lower()=="auth":
            # If the "qop" value is "auth" or "auth-int":
            # request-digest  = <"> < KD ( H(A1),     unq(nonce-value)
            #                              ":" nc-value
            #                              ":" unq(cnonce-value)
            #                              ":" unq(qop-value)
            #                              ":" H(A2)
            #                      ) <">
            if self.backend.passwordStorage == CLEAR_TEXT:
                start = self.H(self.A1(request))
            else:
                start = self._checksum(request)

            #return self.KD(self.H(self.A1(request)), \
            return self.KD(start, \
                           request.env['__DIGEST_PARAMS__']["nonce"]
                           + ":" + request.env['__DIGEST_PARAMS__']["nc"]
                           + ":" + request.env['__DIGEST_PARAMS__']["cnonce"]
                           + ":" + request.env['__DIGEST_PARAMS__']["qop"]
                           + ":" + self.H(":" + request.rawUri))

    def response(self, request):
        if request.env['__DIGEST_PARAMS__'].has_key("qop"):
            # Check? and request.env['__DIGEST_PARAMS__']["qop"].lower()=="auth":
            # If the "qop" value is "auth" or "auth-int":
            # request-digest  = <"> < KD ( H(A1),     unq(nonce-value)
            #                              ":" nc-value
            #                              ":" unq(cnonce-value)
            #                              ":" unq(qop-value)
            #                              ":" H(A2)
            #                      ) <">
            if self.backend.passwordStorage == CLEAR_TEXT:
                start = self.H(self.A1(request))
            else:
                start = self._checksum(request)

            #return self.KD(self.H(self.A1(request)), \
            return self.KD(start, \
                           request.env['__DIGEST_PARAMS__']["nonce"]
                           + ":" + request.env['__DIGEST_PARAMS__']["nc"]
                           + ":" + request.env['__DIGEST_PARAMS__']["cnonce"]
                           + ":" + request.env['__DIGEST_PARAMS__']["qop"]
                           + ":" + self.H(self.A2(request)))
        else:
            # If the "qop" directive is not present (this construction is
            # for compatibility with RFC 2069):
            # request-digest  =
            #         <"> < KD ( H(A1), unq(nonce-value) ":" H(A2) ) > <">
            return self.KD(self.H(self.A1(request)), \
                           request.env['__DIGEST_PARAMS__']["nonce"] + ":" + self.H(self.A2(request)))

    def _parseHeader(self, authheader, request):
        n = 7 # n = len("Digest ")
        try:
            authheader = authheader[n:].strip()
            items = urllib2.parse_http_list(authheader)
            request.env['__DIGEST_PARAMS__'] = urllib2.parse_keqv_list(items)
        except Exception, e:
            request.env['__DIGEST_PARAMS__'] = {}

    def _returnTuple(self, code):
        self.code = code

        if code < 400:
            return True
        else:
            return False

    def _createNonce(self):
        return hashlib.md5("%d:%s" % (time.time(), self.realm)).hexdigest()

    def createAuthheader(self, request):
        request.env['__DIGEST_HEADERS__']["WWW-Authenticate"] = \
            'Digest realm="%s", nonce="%s", algorithm="MD5", qop="auth"' % \
            (self.realm, self._createNonce())

    def _doAuthenticate(self, request):
        """ Check the response for this method and uri with authheader

        returns a tuple with:
          - HTTP_CODE
          - a tuple with header info (key, value) or None
          - and the username which was authenticated or None
        """

        request.env['__DIGEST_HEADERS__'] = {}
        request.env['__DIGEST_PARAMS__'] = {}
        
        if not request.env.get('HTTP_AUTHORIZATION'):
            self.createAuthheader(request)
            return self._returnTuple(401)

        authHeader = request.env['HTTP_AUTHORIZATION']
        if authHeader.strip() == '':
            self.createAuthheader(request)
            return self._returnTuple(401)
        self._parseHeader(authHeader, request)
        if not len(request.env['__DIGEST_PARAMS__']):
            return self._returnTuple(400)
        # Check for required parameters
        required = ["username", "realm", "nonce", "uri", "response"]
        for k in required:
            if not request.env['__DIGEST_PARAMS__'].has_key(k):
                return self._returnTuple(400)
        
        # If the user is unknown we can deny access right away
        # -- if not self.backend.has_key(request.env['__DIGEST_PARAMS__']["username"]):
        if not self._getPassword(request, request.env['__DIGEST_PARAMS__']["username"]):
            self.createAuthheader(request)
            return self._returnTuple(401)
        # If qop is sent then cnonce and cn MUST be present
        if request.env['__DIGEST_PARAMS__'].has_key("qop"):
            if not request.env['__DIGEST_PARAMS__'].has_key("cnonce") \
               and request.env['__DIGEST_PARAMS__'].has_key("cn"):
                return self._returnTuple(400)
        # All else is OK, now check the response.
        if self.response(request) == request.env['__DIGEST_PARAMS__']["response"]:
            self.setIdentity(request, request.env['__DIGEST_PARAMS__']['username'])
            rspauth = self.rspauth(request)
            if (rspauth):
                authInfo = 'rspauth="%s", cnonce="%s", nc=%s, qop=auth' % \
                (rspauth, request.env['__DIGEST_PARAMS__']['cnonce'], request.env['__DIGEST_PARAMS__']['nc'])
                request.setHeader('Authentication-Info', authInfo)
            return self._returnTuple(200)
        else:
            self.createAuthheader(request)
            return self._returnTuple(401)

    def getErrorResponse(self, request):
        body = AuthProvider.getErrorResponse(self, request)[2]
        request.env['__DIGEST_HEADERS__']['Content-Type'] = 'text/html';

        return [ self.code, request.env['__DIGEST_HEADERS__'], body]

import core.coder as coder
class TokenAuthProvider(AuthProvider):
    def __init__(self, *args, **kwargs):
        self.secret = kwargs.pop('secret')
        AuthProvider.__init__(self, *args, **kwargs)

    def _doAuthenticate(self, request):
        try:
            cipher = coder.SecureLink(**self.secret)
            result = cipher.decode(request.uri, ['-rest'])
            methods = result[1]
            identity = result[2]
        except Exception, ex:
            logging.getLogger().warn('Invalid authentication: %s. URL: %s' % (ex,request.uri))
            return False

        if not request.method in methods:
            logging.getLogger().error("Method [%s] is not in methods[%s]: " % (request.method,methods))

            return False

        self.setIdentity(request, identity)
        checkSum = request.postpath.pop(0)
        request.prepath.append(checkSum)
        request.env['auth'] = {}
        request.env['auth']['checksum'] = checkSum
        request.env['auth']['path']     = '/'.join(result[3].split('/')[0:result[4]])
        if request.env['auth']['path'][0:1] != '/':
            request.env['auth']['path'] = '/' + request.env['auth']['path']

        prefixEnd = request.uri.find(request.env['auth']['path'])
        request.env['BASE_URI'] = request.uri[0:prefixEnd]

        #request.postpath = result[3].strip('/').split('/')

        return True