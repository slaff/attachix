import core.notify.dispatcher as notify
import conf.vhosts.available.token as token

class VHost(token.VHost):
    host = ['localhost']
    port = '8181'

    def build(self):
        """
        Build the resource tree
        """
        token.VHost.build(self)

        # [Change the notifiers] #
        if self.config.has_key('notificationPluginDirs'):
            self.root.tree.notifier = notify.Enabled(self.config['notificationPluginDirs'])
        else:
            self.root.tree.notifier = notify.Enabled()