from gevent.pool import Pool
import logging
import os
import core.utils as utils

# Execute maximum 10 concurrent jobs at a time
pool = Pool(10)


class Abstract():
    """
    This method takes care to dispath the event to the plugins that
    are subscribed for it

    @param Resource resource
    @param string event
    @param string uri  - the path in the global resource tree
    @param string path - the local resource path
    @param array meta
    """
    def publish(self, request, resource, path, meta):
        """
        Implement this method in the child class
        """
        pass

class Enabled(Abstract):
    """
    Loads all enabled plugins and notifies them when an event occurs.
    Enabled modules are the ones that can be found in the pluginDirs
    """

    _pluginDirs =  [
        'core/notify/plugins/enabled',
    ]

    _plugins = [
        # plugin object (instance notify.plugins.base)
    ]

    loaded = False

    def __init__(self):
        self.loadPlugins()
    
    def loadPlugins(self, force=False):
        """
        Takes care to (re)load all notification plugins
        """

        if not Enabled.loaded or force == True:
            # Get all plugins from the plugin directories.
            # Load them and init them
            for directory in Enabled._pluginDirs:
                # get  files in the directory
                try:
                    files = os.listdir(directory)
                except:
                    logging.getLogger().warn('Invalid Notification Plugin Directory: %s' % directory)
                    continue

                files.sort()
                for file in files:
                    if file[-3:]!='.py' or file[0:1] == '_':
                        continue
                    klass = utils.require(directory+'/'+file,'Plugin')
                    Enabled._plugins.append(klass())
            Enabled.loaded = True

    """
    This method takes care to dispath the event to the plugins that
    are subscribed for it

    @param Resource resource
    @param string event
    @param string uri  - the path in the global resource tree
    @param string path - the local resource path
    @param array meta
    """
    def publish(self, user, request, resource, path, meta):
        for plugin in Enabled._plugins:
            if plugin.canProcess(request.method, meta):
                # run the jobs in parallel
                pool.spawn(plugin.process, user, request, resource, path, meta)

class UserEnabled(Enabled):
    """
    This method takes care to dispath the event to the plugins that
    are subscribed for it

    @param Resource resource
    @param string event
    @param string uri  - the path in the global resource tree
    @param string path - the local resource path
    @param array meta
    """
    def publish(self, user, request, resource, path, meta):
        plugins = self.getUserPlugins(user,path)
        for plugin in plugins:
            if plugin.canProcess(request.method, meta):
                # run the jobs in parallel
                pool.spawn(plugin.process, user, request, resource, path, meta)

    def getUserPlugins(self, user, path):
        """
        Decides which plugins can be used from the current user for
        the given path based on the user settings.
        """

        """
        # @todo:
        User.Settings.Notification has:
            user
            path
            plugin
            options = {}
        """

        return self._plugins

        # @todo: Implement the user object

        plugins = []
        for notification in user.get('property').notifications:
            if notification.path.startswith(node.path):
                plugins.append(self._plugins[notification.plugin])

        return plugins

class Manual(Abstract):
    """
    Loads plugins and notifies them when a event occurs
    """

    _plugins = [
        # plugin object (instance notify.plugins.base)
    ]

    """
    @param user user
    @param list plugins list of objects instances of notify.plugins.base
    """
    def __init__(self, plugins):
        if type(plugins)!=list:
            raise ValueError("Plugins parameter must be list")
        self._plugins = plugins

    """
    This method takes care to dispath the event to the plugins that
    are subscribed for it

    @param Resource resource
    @param string event
    @param string uri  - the path in the global resource tree
    @param string path - the local resource path
    @param array meta
    """
    def publish(self, user, request, resource, path, meta):
        for plugin in self._plugins:
            if plugin.canProcess(request.method, meta):
                # run the jobs in parallel
                pool.spawn(plugin.process, user, request, resource, path, meta)