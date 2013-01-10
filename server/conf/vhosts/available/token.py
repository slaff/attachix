import core.provider.authentication as authentication
import core.notify.dispatcher as notify
import core.notify.plugins.available.changes as changes
import core.provider.storage as storage
import core.resource.base as resource
import conf.vhosts.available.default as default

class VHost(default.VHost):
    host = ['localhost']
    port = '8888'

    def build(self):
        """
        Build the resource tree
        """
        default.VHost.build(self)

        # [Change the notifiers] #
        self.root.notifier = notify.Manual([changes.Plugin()])

        # plain propfind xslt replaces the other one
        xsltResource = resource.StaticResource(
                            storage.FileStorageProvider(self.config['basePath']+'/static/public/propfind-plain.xslt'),
                            expirationDays = 2
                          )
        xsltResource.isLeaf = True
        self.root.children['~static'].putChild('propfind.xslt', xsltResource)

        tree = resource.TokenAccessResourceDecorator(self.root)

        self.root = resource.TokenResource(
                                authProvider=authentication.TokenAuthProvider(secret=self.config['share']['secret'],
                                             userProvider=self.user
                                             ),
                                tree=tree)