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

    'profile' : {
        # Allow profiling
        'enabled': True,
        'statsOutput': '/tmp/profiler-stats.txt',
        'summaryOutput': None,
        'traceOutput': None,
        'countTimeBlocking': True,
        'printPercentage': True,
        'duration': 60 # Time to gather profiling information
    },

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
    },

    # Default Server Share values
    'share': {
        'host': 'localhost:8888',
        'public_host': 'localhost:8181',
        'methods': ['GET','PROPFIND','OPTIONS'],
        'prefixes': ['.views'],
        'depth': 255,
        'expiration': 86400*30, # 30 days in seconds
        'secret': {
            'key': "\x8d\x8e\x98\xaf\x1c\xe6\xed\x02\x82F\xc81\xd7\x03\x00r\x89\x88'\xe7-\x80Z\x95v\xc7\xf40\x9bvX\xd6",
            'iv' : '.}\x91\xebtT\xd3+\x91\xc2\x1b\x9f\xeb\xb4\xb9z',
            'chKey': "O#XlmP\xd3'B;\xdd\xd55\t\x80\xd6\xa0\xef\x96\xfe(\xc2\x7c\\\xf3\xb8\xc7\x142\xcdQF_\xfa\xb3\xbb\xeb\x06i\x96\xdf\x07\x1c\xb0\x8arV\x9b\xe1{s#\x91\xe9\xb4\xae\x1an\x14\xc71\xee-t\xc2\xce\xd7V\x1e&h9\xcbP\x9bb\xccG\xf60,\xd0s \xe8\xcb\x7f\x85*\xec\x03\x8c\xf9^\xa1?A:q\xa6V\x9bf\xed\xf9\xcb\x81\xc6\xf2\x8e\x08\xdd\xec$\xd3\x8de\xe8z\xffW>9F\x7f[\xf8p\x85\xf5$\xed\x82qt\xc4\x1cp\x8b\xf5\x98\xe5\x19\x08\x9a}\x07=w\xdd\xa9\x8b\x03\x01\xedo~\xe3P\x82\x0c\xe4\xa4\xb4\x0cS\x00\x03\xdd\\\xa7+\x9bfDh\xbeZ\x8c7\x02X*\x1d\xaf\xbeCb\xa7C\x1d@\x91\xa9YK\xf8\xb8/^\x04rE\xd2\xdfh\x16j\xc4\xb1\x9d\xc2\t7\x08\xa6\xddC%\xae0P}\x86\x9c\xc38w\xaey~*l\xd1\\\xf8\x9e\xe1\xcd\x9bG\x86\xef\xcb\xbe\xa6\xcfD\xde\xd6\xd0\r\xa2N\xff"
        },
        'email': {
            'from': 'no-reply-shares@attachix.de',
            'subject': 'Share "%s" in Attachix.de',
            'body': """
User with email #email# has shared folder "#folder#" with you.

You can see the content in your browser by visiting:

http://#url#

Or use the same URL in your webdav client for faster viewing and file operations.
If you need help setting your webdav client, please visit:
http://#url#/~help/webdav/

This invitation is valid until #expirationDate#

(c) 2012 Attachix
""",
            'headers': {
                 'Content-Type' :'text/plain; charset=utf-8',
                 'Content-Transfer-Encoding': '8bit'
             }
        }
    }
}
