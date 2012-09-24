#!/usr/bin/python
"""Moore WSGI server"""
import gevent
import gevent.pool
from gevent import monkey; monkey.patch_all()
from gevent import pywsgi as wsgi
import os
import sys
basePath = os.path.dirname( os.path.realpath( __file__ ) )
libPath = basePath+'/lib'
sys.path.insert(1,libPath)

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
if config.get('debug')==True:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(config.get('logLevel', logging.INFO))

# [Config Profiling] #
if config.has_key('profile') and config['profile'].get('enabled')==True:
    try:
        # If the profiler is available on the system then enable it
        import gevent_profiler
        import signal

        profile = config['profile']
        if profile.has_key('summaryOutput'):
            gevent_profiler.set_summary_output(profile['summaryOutput'])

        if profile.has_key('statsOutput'):
            gevent_profiler.set_stats_output(profile['statsOutput'])

        if profile.has_key('traceOutput'):
            gevent_profiler.set_trace_output(profile['traceOutput'])

        if profile.has_key('printPercentage'):
            gevent_profiler.print_percentages(profile['printPercentage'])

        if profile.has_key('countTimeBlocking'):
            gevent_profiler.time_blocking(profile['countTimeBlocking'])

        gevent_profiler.attach_on_signal(signum=signal.SIGUSR1, duration=profile['duration'])
        logger.info("The profiler is enabled and waiting on signal USR1.")

    except Exception as ex:
        print ex
        pass


if config.has_key('pool'):
    gevent.pool.Pool(config['pool'])

# [ Prepare the application ]
Application.setup(config)

# [ Define the dispatcher ]
def Dispatcher(env, start_response):
    request = Request(env, start_response)
    Application.run(request)

    return request.getResponseBody()

# debug settings
env = {
   # 'wsgi.file_wrapper': wsgi.SendFileWrapper()
}


# [Create Servers] #
servers = []
serverLog = 'default'
if not config.get('logRequests', True):
    serverLog = None
for ip, ports in Application.vhosts.items():
    for port, vhosts in ports.items():
        port = int(port)
        for vhost in vhosts:
            if vhost.ssl['key']:
                # no sendfile for SSL connections... sigh :(
                server = wsgi.WSGIServer((ip, port), Dispatcher, environ={},
                         backlog=config['backlog'],
                         keyfile=vhost.ssl['key'], certfile=vhost.ssl['cert'], log=serverLog)
            else:
                server = wsgi.WSGIServer((ip, port), Dispatcher, environ=env,
                         backlog=config['backlog'],log=serverLog)
            servers.append(server)
            logger.info('Serving on %s:%s ...' % (ip,port))

# [Start Servers] #
gevent.joinall( [gevent.spawn(server.serve_forever) for server in servers ] )
