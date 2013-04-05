# -*- coding: utf-8 -*-
import core.notify.dispatcher as notify
import core.provider.authentication as auth
import core.provider.authentications.backend as authBackend
import core.provider.locking as locking
import core.provider.property as property
import core.provider.storage as storage
from core.provider.users.backend import DummyBackend as DummyUser
import core.resource.base as resource
import core.resource.mvc as mvcResource
import core.vhost as vhost

from experimental.resource.office import CaldavResource, CardavResource

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


        crossdomainResource = resource.StaticResource(
                            storage.FileStorageProvider(self.config['basePath']+'/static/public/crossdomain.xml'),
                            expirationDays= 2
                          )
        crossdomainResource.isLeaf = True
        root.putChild('crossdomain.xml', crossdomainResource)

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

        root.putChild('-rest', mvcResource.RestResource(
                                'core/resource/controller/',
                                auth=self.auth
                              ))

        from experimental.provider.calendar import DummyCalendarProvider
        root.putChild('~calendar', CaldavResource(
                               storage.UserStorageProvider(
                                    path="/tmp/calendar/",
                                    propertyProvider=property.Redis('prop_calendar_'),
                                    nestedLevel=2,
                                    createIfNonExistent=True
                               ),
                               self.locking,
                               self.auth,
                               self.notifier,
                               calendarProvider=DummyCalendarProvider()
                     ))

        from experimental.provider.contact import DummyContactProvider
        root.putChild('~contacts', CardavResource(
                               storage.UserStorageProvider(
                                     path="/tmp/contacts",
                                     propertyProvider=property.Redis(
                                                'prop_contacts_'
                                     ),
                                     nestedLevel=2,
                                     createIfNonExistent=True
                               ),
                               self.locking,
                               self.auth,
                               self.notifier,
                               contactProvider=DummyContactProvider()
                     ))

        self.root = root