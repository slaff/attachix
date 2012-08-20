import shutil
import os
import os.path

class Locator():
    def save(self, localFile, suggestedName=None):
        """
        Saves data to a location
        @return string token for retrieving the file
        """
        return None

    def send(self, data, name=None):
        """
        Sends the data to a location, under certain name, without saving it to local file
        @return string token for retrieving the file
        """
        return None

    def isLocal(self, token):
        """
        Checks if the token is for local file or remote one
        """
        return True

    def retrieve(self, token):
        """
        Returns the URL from where the file can be accessed
        """
        return None

    def delete(self, token):
        """
        Delete the file identified with a given token
        """
        pass

class FileLocator(Locator):
    prefix = None
    
    def __init__(self, prefix):
        self.prefix = prefix

    def save(self, localFile, suggestedName=None):
        """
        Saves data to a location
        @return string token for retrieving the file
        """
        destination = self._translatePath(suggestedName)
        (path, _) = os.path.split(destination)
        if not os.path.exists(path):
            os.makedirs(path)

        shutil.move(localFile, destination)

        return destination

    def send(self, data, name=None):
        """
        Sends the data to a location, under certain name, without saving it to local file
        @return string token for retrieving the file
        """
        raise ValueError('Not Implemented')

    def isLocal(self, token):
        """
        Checks if the token is for local file or remote one
        """
        return True

    def retrieve(self, token):
        """
        Returns the URL from where the file can be accessed
        """
        return token

    def delete(self, token):
        """
        Delete the file identified with a given token
        """
        os.remove(token)

    def _translatePath(self, path):
        return self.prefix+'/'+path


class NestedFileLocator(FileLocator):

    def __init__(self, prefix, nestingLevel=3):
        FileLocator.__init__(self, prefix)
        self.nestingLevel = nestingLevel

    def _translatePath(self, path):
        parts = path.lstrip('/').split('/')
        parts[0] = "%s/%s/%s" % (parts[0][0:4], parts[0][4:8], parts[0][8:12])
        path = '/'.join(parts)
        return self.prefix+'/'+path

# @todo: add here the MogileFS locator (tracker)
# @todo: add here the HadoopFS locator

