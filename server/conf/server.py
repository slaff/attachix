"""
Server configuration File
"""
import logging

Config = {
    'realm': 'Private Area',

    # defines the maximum greenlets per server
    'pool'   : 150,
    'backlog': 150,
    'debug': True,
    'logLevel': logging.INFO,

    # The root directory that will contain the user data
    'dataFolder': '/',
   
    'pool': {
        'hypertable': {
           'host': 'localhost',
	   'namespace': 'moore'
        },
        'redis': {
            'maxSize': 150
        }
    }
}
