import logging
import hashlib
import os.path
import re
import time

from core.http import normalizeUri
from core.coder import Secure
from core.coder import SecureLink
from core.root import Resolver
import conf.server as config

from django.core import mail
from django.conf import settings
try:
	settings.configure(DEBUG=True)
except Exception, ex:
	logging.getLogger().error('Django config error: %s' % ex);


from django.core.validators import email_re

"""
User Controller
"""
class User():
    auth = None
    cipher = None

    def __init__(self, auth):
        self.auth = auth
        self.cipher = Secure(config.Config['secret']['key'],
                             config.Config['secret']['iv']
                             )

    def post_Share(self, request):
        user = self.getUser(request)
        
        path = request.params['path']
        path = re.sub(r'/{2,}', '/', path)
        toEmail  = request.params['to_email']
        days      = 30
        if request.params.has_key('days'):
            days = int(request.params['days'])

        cipher = SecureLink(**config.Config['secret'])
        tokenURL = config.Config['tokenHost'] + '/' + cipher.encode(['GET','PROPFIND','OPTIONS'],
                                               user.getIdentity(),
                                               path,
                                               ['.views'],
                                               255,
                                               expiration=86400*days
                                              )

        
        fromEmail = user.getIdentity()

        shareName = normalizeUri(os.path.basename(path))
        if shareName == '':
            shareName = '/'
        elif len(shareName) > 30:
            shareName = shareName[0:27]+'...'

        body = """
User with email %s has shared folder "%s" with you.

You can see the content in your browser by visiting:

http://%s

Or use the same URL in your webdav client for faster viewing and file operations.
If you need help setting your webdav client, please visit:
http://%s/~help/webdav/

This invitation is valid in the next %d day(s)

(c) 2011 Attachix 
""" % (fromEmail, shareName, tokenURL, tokenURL, days)

        if not email_re.match(fromEmail):
            fromEmail = 'no-reply-shares@attachix.de'

        logging.getLogger().debug('post_Share: %s' % body )

        # send the email
        email = mail.EmailMessage(
                    subject='Share "%s" in Attachix.de' % shareName,
                    body=body,
                    from_email=fromEmail,
                    to=[toEmail],
                    headers = {
                        'Content-Type' :'text/plain; charset=utf-8',
                        'Content-Transfer-Encoding': '8bit'
                    }
                )
        try:
            email.send()
        except:
            return {'code':'failure', 'body': 'Unable to send email. Please try again later.'}

        return {'body': 'Share invitation was send successfully.'}


    def getUser(self, request):
        if request.env.has_key('user'):
            return request.env['user']

        if self.auth is None:
            return None

        if request.params.get('_silent'):
            if not self.auth.hasData(request):
                return None

        if not self.auth.authenticate(request):
            return None

        request.env['user'] = self.auth.getUser(request)
        
        return request.env['user']
