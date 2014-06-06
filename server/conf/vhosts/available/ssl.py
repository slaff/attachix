import core.provider.authentication as auth
import core.provider.authentications.backend as authBackend
import conf.vhosts.available.default as default

class VHost(default.VHost):
    port = 8443
    ssl  = {
        'keyfile': 'conf/ssl/moore.io.key',
        'certfile': 'conf/ssl/moore.io.pem'
    }

    def load(self):
         default.VHost.load(self)
         self.auth = auth.BasicAuthProvider(self.config['realm'],
                                            authBackend.Md5FileBackend(
                                                file=self.config['basePath']+'/static/private/md5_passwd',
                                            ),
                                            userProvider=self.user
                     )
