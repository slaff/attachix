#!/usr/bin/python
"""
Script that simplifies the task of adding new users.
"""

import hashlib
import sys

if len(sys.argv)!=4:
    print "Usage:\n\t%s <user> <realm> <pass>" % sys.argv[0]
    sys.exit(0);

username = sys.argv[1]
realm = sys.argv[2]
passwd = sys.argv[3]

secret = "%s:%s:%s" % (username, realm, passwd)
print "%s:%s\n" % (username, hashlib.md5(secret).hexdigest())