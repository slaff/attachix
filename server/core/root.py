"""
Root Resource and Resolver Classes
"""

from http import BaseRequest, normalizeUri

class Resolver():
    root = None
    duplicate = None

    @staticmethod
    def setRoot(root):
        """
        Sets the root of the tree used for uri resolving
        """
        Resolver.root = root

    @staticmethod
    def getResourceForRequest(request,tree=None):
        """
        Traverse resource tree to find who will handle the request.
        """
        if tree is not None:
            resource = tree
        else:
            resource = Resolver.root
        lastObjectId = "%s" % resource
        request.path = '/'
        while request.postpath and not resource.isLeaf:
            pathElement = request.postpath.pop(0)
            request.prepath.append(pathElement)
            resource = resource.getChildWithDefault(pathElement, request)
            currentObjectId = "%s" % resource
            if lastObjectId != currentObjectId:
                request.path = '/'
                lastObjectId = currentObjectId
            else:
                request.path += pathElement + '/'
        if len(request.path) > 1:
            # remove the trailing slash
            request.path = request.path[:-1]
        return resource
        
    @staticmethod
    def getResourcePathForUri(uri, tree=None):
        """
        Traverse resource tree to find who will handle the request.
        @return list - [resource, path in the resource]
        """
        request = BaseRequest(uri)
        resource = Resolver.getResourceForRequest(request, tree)
        return [resource, request.path]
    


class Resource():
    isLeaf = 0
    children = {}

    def __init__(self):
        self.children = {}
        self.isLeaf   = 0

    def putChild(self, path, child):
        """
        Register static child
        """
        self.children[path] = child
        return child

    def getChild(self, path, request):
        """
        Put the login in the extending class
        """
        pass

    def render(self, request):
        try:
            m = getattr(self, 'render_'+request.method)
        except AttributeError:
            request.setHeader('Content-Type', 'text/plain')
            request.writeDirect('',400)
            return

        return m(request)

    def getChildWithDefault(self, path, request):
        if path in self.children:
            return self.children[path]
        return self.getChild(path, request)

    def redirect(self, request, uri):
        """
        Makes internal redirect into the resource tree
        """
        uri = normalizeUri(uri)
        request.prepath = []
        request.postpath = string.split(request.uri[1:], '/')