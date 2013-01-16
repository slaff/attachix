import os
import sys
import StringIO
import unittest
sys.path.insert(0,'../../')
sys.path.insert(1,'../../lib/')

import core.coder as coder
import conf.vhosts.available.token as token
import conf.server as serverConfig

from core.http import BaseRequest
from core.resource import Resolver

class ResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.config = serverConfig.Config
        basePath = os.path.dirname( os.path.realpath( __file__ ) )+'/../../'
        if not self.config.has_key('basePath'):
            self.config['basePath'] = basePath

        self.cipher = coder.SecureLink(**self.config['share']['secret'])


    def testTokenResource(self):
        vhost = token.VHost(self.config)
        vhost.load()
        vhost.build()

        properties = {
            '{custom-namespace:}test': 'value'
        }

        # [Patch properties] #
        uri = "/"+self.cipher.encode(['PROPFIND','PROPPATCH'], 1, '/tmp', [], 0)
        data = """<?xml version="1.0"?>
<d:propertyupdate xmlns:d="DAV:">
  <d:set>
    <d:prop>"""
        for property, value in properties.items():
            nameSpace = "system:" # the default namespace
            if property[0] == '{':
                pos = property.find('}')
                nameSpace = property[1:pos]
                key = property[pos + 1:]
            else:
                key = property[0]
            
            data += "<%s xmlns=\"%s\">%s</%s>" % (key, nameSpace, value, key)

        data += """
        </d:prop>
    </d:set>
</d:propertyupdate>"""

        env = {
            'REQUEST_METHOD': 'PROPPATCH',
            'wsgi.input': StringIO.StringIO(data),
            'cache': {}
        }
        request = BaseRequest(uri, env)
        resource = Resolver.getResourceForRequest(request, vhost.root)
        resource.render(request)

        self.assertEquals(request._responseCode,207, request.getResponseBody())

        # [Find properties] #
        data = """<?xml version="1.0"?>
<d:propfind xmlns:d="DAV:">
    <d:prop>"""
        for property, value in properties.items():
            nameSpace = "system:" # the default namespace
            if property[0] == '{':
                pos = property.find('}')
                nameSpace = property[1:pos]
                key = property[pos + 1:]
            else:
                key = property[0]

            data += "<%s xmlns=\"%s\" />" % (key, nameSpace)

        data += """</d:prop>
</d:propfind xmlns:d="DAV:">
        """
        
        env = {
            'REQUEST_METHOD': 'PROPFIND',
            'HTTP_DEPTH': '0',
            'wsgi.input': StringIO.StringIO(data),
            'cache': {}
        }

        request = BaseRequest(uri, env)
        resource = Resolver.getResourceForRequest(request, vhost.root)
        resource.render(request)

        self.assertEquals(request._responseCode,207, request.getResponseBody())

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()