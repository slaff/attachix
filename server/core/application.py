import logging
import os
from core.resource import Resolver
import utils

class Application():
    auth = None
    locking  = None
    config = None

    vhostDirs = ['conf/vhosts/enabled']
    vhosts = []
    lookup = {}
    defaultHost = {}

    @staticmethod
    def setup(config):
        """
        Load the Vhosts
        """

        for directory in Application.vhostDirs:
            # get  files in the directory
            try:
                files = os.listdir(directory)
            except Exception as ex:
                logging.getLogger().warn('Invalid VHosts Directory: %s. Error: %s' % (directory,ex))
                continue

            # vhosts[ip][port][i]= vhost
            vhosts = {}
            lookup = {}
            files.sort()
            for file in files:
                if file[-3:]!='.py' or file[0:1] == '_':
                    continue
                klass = utils.require(directory+'/'+file,'VHost')
                vhost = klass(config)
                vhost.load()
                vhost.build()
                if not vhosts.has_key(vhost.ip):
                    vhosts[vhost.ip] = {}
                if not vhosts[vhost.ip].has_key(vhost.port):
                    vhosts[vhost.ip][vhost.port] = []

                iPort = int(vhost.port)
                if not Application.defaultHost.has_key(iPort):
                    Application.defaultHost[iPort] = vhost

                pos = len(vhosts[vhost.ip][vhost.port])
                vhosts[vhost.ip][vhost.port].append(vhost)

                for host in vhost.host:
                    # @todo: the order is missing here
                    lookup["%s:%s:%s" % (host, vhost.port, vhost.ip)] = vhosts[vhost.ip][vhost.port][pos]

            Application.vhosts = vhosts
            Application.lookup = lookup

    @staticmethod
    def run(request):
        try:
            hostHeader = request.env['HTTP_HOST']
        except KeyError:
            request.setResponseCode(400)
            request.finish()
            return
            
        try:
            cut = hostHeader.index(':')
            hostHeader = hostHeader[:cut]
        except ValueError:
            pass
        
        host = "%s:%s:%s" % (hostHeader, request.env['SERVER_PORT'], request.env['SERVER_NAME'])
        fallbackHost = "%s:%s:0.0.0.0" % (hostHeader, request.env['SERVER_PORT'])

        # define the default host
        vhost = Application.defaultHost[int(request.env['SERVER_PORT'])]
        hostToUse = None
        if Application.lookup.has_key(host):
            hostToUse = host
        elif Application.lookup.has_key(fallbackHost):
            hostToUse = fallbackHost

        if hostToUse:
            vhost = Application.lookup[hostToUse]

        resource = Resolver.getResourceForRequest(request, vhost.root)
        request.env['VHOST'] = {
            'root': vhost.root,
            'host': hostToUse
        }
        resource.render(request)
        if request.getState()!=3:
            request.finish()
