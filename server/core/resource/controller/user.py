import logging
import hashlib
import os.path
import re
import time
import datetime

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
        self.cipher = Secure(config.Config['share']['secret']['key'],
                             config.Config['share']['secret']['iv']
                             )

    def post_Share(self, request):
        user = self.getUser(request)
        shareConfig = config.Config['share']
        
        path = request.params['path']
        path = re.sub(r'/{2,}', '/', path)
        toEmail  = request.params['to_email']
        expiration      = shareConfig['expiration']
        if request.params.get('days'):
            expiration = 86400 * int(request.params['days'])

        cipher = SecureLink(**shareConfig['secret'])
        tokenURL = shareConfig['host'] + '/' + cipher.encode(shareConfig['methods'],
                                               user.getIdentity(),
                                               path,
                                               shareConfig['prefixes'],
                                               255,
                                               expiration=expiration
                                              )

        
        fromEmail = user.getIdentity()

        shareName = normalizeUri(os.path.basename(path))
        if shareName == '':
            shareName = '/'
        elif len(shareName) > 30:
            shareName = shareName[0:27]+'...'

        body = shareConfig['email']['body']
        vars = {
            'email':fromEmail,
            'folder': shareName,
            'url': tokenURL,
            'expirationDate': datetime.datetime.fromtimestamp(time.time()+expiration).strftime('%Y-%m-%d %H:%M:%S')
        }
        for (key, value) in vars.items():
            body=body.replace("#%s#" % key, value)

        if not email_re.match(fromEmail):
            fromEmail = shareConfig['email']['from']

        logging.getLogger().debug('post_Share: %s' % body )

        # send the email
        email = mail.EmailMessage(
                    subject=shareConfig['email']['subject'] % shareName,
                    body=body,
                    from_email=fromEmail,
                    to=[toEmail],
                    headers = shareConfig['email']['headers']
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
