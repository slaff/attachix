import core.notify.dispatcher as notify
import core.provider.authentication as auth
import core.provider.authentications.backend as authBackend
import core.provider.locking as locking
import core.provider.property as property
import core.provider.storage as storage
from core.provider.users.backend import DummyBackend as DummyUser
import core.resource.base as resource
import core.vhost as vhost

class VHost(vhost.VHost):
    host = ['localhost']
    ip   = '127.0.0.1'
    port = '8088'

    def load(self):
        """
        Init The Application
        """
        # [Set up the user provider] #
        self.user = DummyUser()

        # [Set up the authentication provider] #
        self.auth = auth.DigestAuthProvider(self.config['realm'],
                                            authBackend.Md5FileBackend(
                                                file=self.config['basePath']+'/static/private/md5_passwd',
                                            ),
                                            userProvider=self.user
                    )

        # [Load The Notification Plugins] #
        if self.config.has_key('notificationPluginDirs'):
            self.notifier = notify.Enabled(self.config['notificationPluginDirs'])
        else:
            self.notifier = notify.Enabled()

        # [Set up the locking provider] #
        self.locking = locking.RedisLockProvider()


    def build(self):
        # [Build the resource tree] #
        # add the root element
        root = resource.WebdavResource(
                               storage.StorageProvider(path=self.config['dataFolder']),
                               self.locking,
                               self.auth,
                               self.notifier
                                      )

        # plus the default favourite icon
        faviconResource = resource.StaticResource(
                            storage.FileStorageProvider(self.config['basePath']+'/static/public/favicon.ico'),
                            expirationDays= 2
                          )
        faviconResource.isLeaf = True
        root.putChild('favicon.ico', faviconResource)

        # the help resource
        root.putChild('~help',
            resource.LimitedResourceDecorator(
                resource.WebdavResource(
                    storage.StorageProvider(self.config['basePath']+'/static/public/help',
                    propertyProvider=property.Redis('properties_help_')

                ), None),
                ['OPTIONS','GET','PROPFIND']
            )
        )

        # and the static files
        root.putChild('~static', resource.StaticResource(storage.StorageProvider(self.config['basePath']+'/static/public'), expirationDays = 2))
        root.putChild('~js', resource.StaticResource(storage.StorageProvider('../clients/jsfront/'), expirationDays=2))

        self.root = root