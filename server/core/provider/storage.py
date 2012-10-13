# -*- coding: utf-8 -*-
import logging
import os
import os.path
import shutil
import stat

import core.provider.property as property
import core.utils as utils

PRECONDITION_FAILED = 17
NOT_FOUND           = 2

class StorageProvider():
    path = None
    CHUNK_SIZE = 16384 # 16KB buffer
    propertyProvider = None # Properties Provider
    
    def __init__(self, path, propertyProvider=property.Base()):
        self.path = path
        self.propertyProvider = propertyProvider

    def get(self, uri, **kwargs):
        return open(self._translateUri(uri, **kwargs))

    def exists(self, uri, **kwargs):
        """
        Checks if the storage node for a given resource
        is existing
        """
        return os.path.exists(self._translateUri(uri, **kwargs))

    def isCollection(self, uri, **kwargs):
        return os.path.isdir(self._translateUri(uri, **kwargs))

    def getMeta(self, uri, depth=0, list=None, **kwargs):
        """
        Gets the live + dead properties of an object
        """        
        uris = [uri]
        if depth > 0 and self.isCollection(uri, **kwargs):
            resources = os.listdir(self._translateUri(uri, **kwargs))
            prefix = uri
            if uri != '/':
                prefix += '/'
            for resource in resources:
                uris.append(prefix + resource)

        meta = {}

        for href in uris:
            path = self._translateUri(href, **kwargs)

            meta[href] = self.propertyProvider.get(path)

            if meta[href].has_key('{DAV:}resourcetype'):
                if meta[href]['{DAV:}resourcetype'] == '':
                    meta[href]['{DAV:}resourcetype'] = 0
                else:
                    meta[href]['{DAV:}resourcetype'] = int(meta[href]['{DAV:}resourcetype'])

            props = {}
            if not meta[href].has_key('{DAV:}getcontenttype'):
                mime_type, encoding = utils.getMime(path)
                props.update({'{DAV:}getcontenttype': mime_type})
                if encoding is not None:
                    props.update({'{DAV:}encoding': encoding})

            if not meta[href].has_key('{DAV:}getcontentlength'):
                stats = os.stat(path)
                dir   = stat.S_ISDIR(stats.st_mode)
                if dir:
                    dir = 1
                    mime_type = 'application/x-directory'
                else:
                    dir = 0
                    
                props.update({
                    '{DAV:}getlastmodified': stats.st_mtime,
                    '{DAV:}getcontentlength': stats.st_size,
                    '{DAV:}creationdate': stats.st_ctime,
                    '{DAV:}resourcetype': dir
                })

            meta[href].update(props)
            for field, value in props.items():
                self.propertyProvider.set(path, field, value)

        return meta

    def setMeta(self, uri, hashes, depth=0, **kwargs):
        if hashes is not None and not isinstance(hashes,dict):
            raise ValueError("Second parameter must be dictionary")

        logging.getLogger().debug("setMeta(%s): %s" % (uri, hashes))
        path = self._translateUri(uri, **kwargs)

        for key, value in hashes.items():
            self.propertyProvider.set(path,key,value)

    def delMeta(self, uri, keys=None,**kwargs):
        if keys is not None and not isinstance(keys,list):
            raise ValueError("Second parameter must be list")

        logging.getLogger().debug("delMeta(%s): %s" % (uri, keys))
        path = self._translateUri(uri, **kwargs)
        if keys is None:
            self.propertyProvider.delete(path)
        else:
            for key in keys:
                self.propertyProvider.delete(path, key)

    def create(self, uri, data, env=None, expectedSize=None, **kwargs):
        localPath = self._translateUri(uri, **kwargs)
        
        self._saveToFile(data,localPath, expectedSize)

        mime_type, encoding = utils.getMime(localPath)
        stats = os.stat(localPath)
        return {
                  '{DAV:}getcontenttype': mime_type,
                  '{DAV:}encoding': encoding,
                  '{DAV:}getcontentlength': stats.st_size,
                  '{DAV:}getlastmodified' : stats.st_mtime,
                }

    def createCollection(self, uri, **kwargs):
        os.mkdir(self._translateUri(uri, **kwargs))

    def copy(self, sourceUri, targetUri, depth=0, **kwargs):
        """
        Copy the source data to the destination
        """
        logging.getLogger().warn("@todo: Handle the depth value")
        if(self.isCollection(sourceUri, **kwargs)):
            shutil.copytree(self._translateUri(sourceUri,**kwargs), self._translateUri(targetUri, **kwargs))
        else:
            shutil.copy2(self._translateUri(sourceUri, **kwargs), self._translateUri(targetUri, **kwargs))

    def move(self, sourceUri, targetUri, depth=0, **kwargs):
        """
        Move the source data to the destination
        """
        logging.getLogger().warn("@todo: Handle the depth value")
        shutil.move(self._translateUri(sourceUri, **kwargs), self._translateUri(targetUri, **kwargs))

    def delete(self, uri, **kwargs):
        if self.isCollection(uri, **kwargs):
            shutil.rmtree(self._translateUri(uri, **kwargs))
        else:
            os.unlink(self._translateUri(uri, **kwargs))
        
        # remove also the views directory
        try:
            shutil.rmtree(self._translateUri(self._translateUri('/.views/' + uri, **kwargs),**kwargs))
        except:
            # @todo: log errors when removing views
            pass

    def getSize(self, uri, depth, **kwargs):
        """
        Gets the total size of the resources
        """
        size = 0
        meta = self.getMeta(uri, -1, None, **kwargs)
        for path, data in meta.items():
            if data['{DAV:}resourcetype']:
                continue
            size += int(data['{DAV:}getcontentlength'])

        return size

            
    def _translateUri(self, uri, **kwargs):
        """
        Translates URI to local path
        """
        return self.path + uri

    def getView(self, uri, request, **kwargs):
        """
        Returns the local path where the views/thumbnails have
        to be stored and the remote url to access it.
        """
        viewURL = '/.views'+uri.replace(request.path,request.uri)
        viewPath = self._translateUri('/.views'+uri, **kwargs)

        return [viewPath, viewURL]


    def _saveToFile(self, data, localPath, expectedSize=None):
        if hasattr(data, 'save_as'):
            data.save_as(localPath)
        else:
            from multipart import copy_file
            if not hasattr(data,'read'):
                import cStringIO as StringIO
                data = StringIO.StringIO(data)
            f = open(localPath,"w")
            if f:
                copy_file(data, f)
                f.close()
        if expectedSize is not None:
            actualSize = os.path.getsize(localPath)
            if actualSize != expectedSize:
                raise ValueError('_saveToFile: Size error. Expected: %s, Actual: %s' % (expectedSize, actualSize))


class UserStorageProvider(StorageProvider):

    def __init__(self, path, propertyProvider=property.Base(), nestedLevel=0, createIfNonExistent=False):
        self.nestedLevel = nestedLevel
        self.createIfNonExistent = createIfNonExistent
        StorageProvider.__init__(self,path,propertyProvider)

    def getNestedName(self, name, nestedLevel, step=2):
        if not len(name):
            raise Exception('Invalid value for parameter identity')
        folder =  ''
        max = len(name)
        for i in range(0,nestedLevel):
            i=i*step
            if i> max-step:
                i = max-step
            folder +='/'+name[i:i+step]
        folder +='/'+name
        return folder

    def _translateUri(self, uri, **kwargs):
        """
        Translates URI to local path
        """
        user = kwargs['user']
        if user.has_key('folder'):
            folder = user['folder']
        else:
            folder =  self.path + '/' + \
                      self.getNestedName(user.getIdentity(),self.nestedLevel)

            if self.createIfNonExistent and not os.path.exists(folder):
                os.makedirs(folder)

        return folder + uri

import core.pool.Redis as Redis
import ujson as json
from core.pattern import Decorator
import re
class CacheDecorator(Decorator):

    def __init__(self, obj, expiration=86400, prefix='storage_meta_'):
        Decorator.__init__(self, obj)
        object.__setattr__(self, "redis", Redis.ConnectionPool().get())
	object.__setattr__(self, "expiration", expiration)
        object.__setattr__(self, "prefix", prefix)

    def getMeta(self, uri, depth=0, list=None, **kwargs):
        meta = {}

        if depth == 0:
            (key, field) = self.getCacheKey(uri, **kwargs)
            data = self.redis.hget(key, field)
            if data:
                meta[uri] = data
        else:
            (key, field) = self.getCacheKey(uri+'/', **kwargs)
            data = self.redis.hgetall(key)
            if data:
                for (name, value) in data.items():
                    if name != '':
                        name = '/'+name
                    meta[uri+name] = value

        if not kwargs.get('generateCache') and len(meta):
            theMeta = {}
            if meta.has_key(uri): # sanity check
                for name, data in meta.items():
                    theMeta[name] = json.decode(data)
                return theMeta

        meta = self._obj.getMeta(uri, depth, list, **kwargs)

        # if the depth == 0 and the main uri is a collection - do not cache
        if kwargs.get('generateCache') or \
        not (depth == 0 and int(meta[uri]['{DAV:}resourcetype'])):
            logging.getLogger().debug("Saving: Keys %s" % meta.keys())
            for (path,data) in meta.items():
                if depth ==0 and uri == path:
                    href = uri
                else:
                    href = path.replace(uri,'')
                logging.getLogger().debug("Saving Key %s %s" % (key, os.path.basename(href)) )
                self.redis.hset(key, os.path.basename(href), json.encode(data))
            self.redis.expire(key, self.expiration)
        
        return meta

    def delMeta(self, uri, list=None, **kwargs):
        self._obj.delMeta(uri, list, **kwargs)
        self.delCache(uri, **kwargs)

    def setMeta(self, uri, hashes, depth=0, **kwargs):
        self._obj.setMeta(uri, hashes, depth, **kwargs)
        self.addCache(uri, **kwargs)

    def create(self, uri, data, env=None, expectedSize=None, **kwargs):
        self._obj.create(uri, data, env, expectedSize, **kwargs)
        self.addCache(uri, **kwargs)

    def createCollection(self, uri, **kwargs):
        self._obj.createCollection(uri, **kwargs)
        self.addCache(uri, **kwargs)

    def move(self, sourceUri, targetUri, depth=0, **kwargs):
        self._obj.move(sourceUri, targetUri, depth, **kwargs)
        self.delCache(sourceUri, **kwargs)
        self.addCache(targetUri, **kwargs)

    def addCache(self, uri, **kwargs):
        (key, field) = self.getCacheKey(uri, **kwargs)
        if self.redis.exists(key):
            """
            The resource is added to the cache only if the
            parent entry has already cache. Otherwise
            the cache will be generated on demand.
            """
            kwargs['generateCache'] = 1
            self.getMeta(uri, 0, None, **kwargs)

    def delCache(self, uri, **kwargs):
        (key, field) = self.getCacheKey(uri, **kwargs)
        self.redis.hdel(key, field)

        (key, field) = self.getCacheKey(uri+'/', **kwargs)
        self.redis.delete(key)


    def getCacheKey(self, uri, **kwargs):
        """
        @param string uri
        @returns [key, field]
        """
        uri = re.sub(r'/{2,}', '/', uri)
        [dir, name] = os.path.split(uri)
        key = '%s%s%s' % (self.prefix, kwargs.get('user').getIdentity(), dir)
        return [key, name]

    def __del__(self):
        # delete object references manually
        object.__delattr__(self, 'redis')
        Decorator.__del__(self)

class FileStorageProvider(StorageProvider):
    """
    Single File Storage Provider.
    """
    def _translateUri(self, uri, **kwargs):
        """
        Translates URI to local path
        """
        return self.path
