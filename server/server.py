#!/usr/bin/python
"""Moore WSGI server"""
import gevent
import gevent.pool
from gevent import monkey; monkey.patch_all()
#from gevent import pywsgi as wsgi
import os
import sys
import signal
basePath = os.path.dirname( os.path.realpath( __file__ ) )
libPath = basePath+'/lib'
sys.path.insert(1,libPath)

import raw_wsgi as wsgi

from core.application import Application
from core.wsgi import Request

import logging
import logging.config

# [Load Server Configuration] #
import conf.server
config = conf.server.Config;

if not config.has_key('basePath'):
    config['basePath'] = basePath

# [Init The Logger] #
logging.config.fileConfig(basePath+'/conf/log.cfg')
logger = logging.getLogger()

# [Config the core] #
import core.instrument

if config.get('debug')==True:
    logger.setLevel(logging.DEBUG)
    signal.signal(signal.SIGUSR1, core.instrument.dumpOnSignal)
else:
    logger.setLevel(config.get('logLevel', logging.INFO))

if config.has_key('profile') and config['profile'].get('enabled')==True:
    core.instrument.enableProfiler(signal.SIGPROF, config['profile'])

if config.has_key('pool'):
    gevent.pool.Pool(config['pool'])

# [ Prepare the application ]
Application.setup(config)

# [ Define the dispatcher ]
def Dispatcher(env, start_response):
    request = Request(env, start_response)
    Application.run(request)

    return request.getResponseBody()

# [Create Servers] #
servers = []
serverLog = 'default'
if not config.get('logRequests', True):
    serverLog = None
for ip, ports in Application.vhosts.items():
    for port, vhosts in ports.items():
        port = int(port)
        for vhost in vhosts:
            server = wsgi.WSGIServer((ip, port), Dispatcher, environ={},
                     backlog=config['backlog'],
                     log=serverLog, **vhost.ssl)
            servers.append(server)
            logger.info('Serving on %s:%s ...' % (ip,port))

# [Start Servers] #
gevent.joinall( [gevent.spawn(server.serve_forever) for server in servers ] )