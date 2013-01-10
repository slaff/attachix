# -*- coding: utf-8 -*-
"""
Package with the Base resource classes
"""
import logging
import math
import os
import os.path
import re
import time
import traceback
from urllib import quote as urlquote
from urllib2 import HTTPError
from urllib2 import Request
from urllib2 import urlopen
import urlparse
import xml.etree.cElementTree as ET

from core.http import fixMimeType
from core.http import getResponseType
from core.http import stringToDatetime
from core.http import parseRangeHeader
from core.http import normalizeUri
from core.properties import createMutlipartResponse
from core.provider.locking import SCOPE_EXCLUSIVE
from core.provider.locking import SCOPE_SHARED
from core.provider.locking import TYPE_READ
from core.provider.locking import TYPE_WRITE
import core.provider.storage as storage
from core.resource import Resolver
from core.resource import Resource
from core.utils import OrderedDict
from core.utils import baseName
from core.utils import StreamRange
import ujson as json

class StaticResource(Resource):
    storageProvider = None
    authProvider    = None
    allowDirectoryListing  = False
    indexFiles             = []
    expirationDays = 0

    def __init__(self,
                 storageProvider,
                 authProvider=None,
                 expirationDays=0,
                 indexFiles=['index.html'],
                 contentDisposition="inline"):
        Resource.__init__(self)
        self.storageProvider = storageProvider
        self.authProvider    = authProvider
        self.expirationDays  = expirationDays
        if indexFiles:
            self.indexFiles = indexFiles
        else:
            self.indexFiles             = []
        self.allowDirectoryListing = False
        self.expirationDays = 0
        self.contentDisposition = contentDisposition # attachment or inline are the valid values for now

    def render(self, request):
        # Authenticate the user first
        if self.authProvider and not request.env.has_key('user'):
            if not self.authProvider.authenticate(request):
                return
            request.env['user'] = self.authProvider.getUser(request)
        try:
            result = Resource.render(self, request)
        except Exception, ex:
            logging.getLogger().debug(traceback.format_exc())
            raise ex

        return result

    def getChild(self, path, request):
        return self

    def render_GET(self, request):
        """
        Get a resource data
        """
        try:
            if not self.allowDirectoryListing and \
            self.storageProvider.isCollection(request.path, user=request.env.get('user'), cache=request.env['cache']):
                # check if at least one of the index files is existing..
                for file in self.indexFiles:
                    if self.storageProvider.exists(request.path+'/'+file, user=request.env.get('user'), cache=request.env['cache']):
                        request.path += '/'+file
                        return self.render_GET(request)
                    
                request.writeDirect('<h1>Directory Listing Is Forbidden', 403)
                return
        except IOError, e:
            if e.errno == 2:
                request.setResponseCode(404)
            else:
                request.setResponseCode(403)
            return

        request.setHeader('Accept-Ranges', 'bytes')
        try:
            stream = self.storageProvider.get(request.path, user=request.env.get('user'), cache=request.env['cache'])
            meta   = self.storageProvider.getMeta(request.path, user=request.env.get('user'), cache=request.env['cache'])
        except IOError, e:
            logging.getLogger().error("render_GET: %s" % traceback.format_exc())

            if e.errno == 2:
                request.writeDirect('<h1>Not Found</h1>',404)
            else:
                request.writeDirect('<h1>Forbidden</h1>',403)
            return

        if meta[request.path].has_key('{DAV:}getetag'):
            if request.env.has_key('HTTP_IF_NONE_MATCH'):
                # @see: http://en.wikipedia.org/wiki/HTTP_ETag
                if request.env['HTTP_IF_NONE_MATCH'].strip('"') == meta[request.path]['{DAV:}getetag']:
                    request.setResponseCode(304)
                    return
            request.setHeader('ETag','"%s"' % meta[request.path]['{DAV:}getetag'])

        if meta[request.path].has_key('{DAV:}getlastmodified'):
            meta[request.path]['{DAV:}getlastmodified'] = float(meta[request.path]['{DAV:}getlastmodified'])
            if request.env.has_key('HTTP_IF_MODIFIED_SINCE'):
                lastModified = long(math.floor(meta[request.path]['{DAV:}getlastmodified']))
                try:
                    modifiedSince = 0
                    try:
                        firstPart = request.env['HTTP_IF_MODIFIED_SINCE'].split(';', 1)[0]
                        modifiedSince = stringToDatetime(firstPart)
                    except:
                        pass
                    
                    if modifiedSince >= lastModified:
                            request.setResponseCode(304)
                            return 

                except ValueError, e:
                    # ignore the if-modified-since header
                    logging.getLogger().debug('Got wrong If-Modified-Since: %s' % e)
                    pass

            request.setHeader('Last-Modified',
                              time.strftime('%a, %d %m %Y %H:%M:%S',
                              time.gmtime(meta[request.path]['{DAV:}getlastmodified'])) + ' GMT')

            if self.expirationDays:
                request.setHeader('Expires',
                              time.strftime('%a, %d %m %Y %H:%M:%S',
                              time.gmtime(meta[request.path]['{DAV:}getlastmodified']+self.expirationDays*86400)) + ' GMT')

        if meta[request.path].get('{DAV:}getcontenttype'):
            meta[request.path]['{DAV:}getcontenttype'] = fixMimeType(request.path, meta[request.path]['{DAV:}getcontenttype']);
            contentType = meta[request.path]['{DAV:}getcontenttype']
            if meta[request.path].has_key('{DAV:}encoding') and \
            meta[request.path]['{DAV:}encoding'] != 'binary':
                contentType += '; charset="%s"' % meta[request.path]['{DAV:}encoding']
            request.setHeader('Content-Type', contentType.encode('ascii'))

        if self.contentDisposition:
            request.setHeader('Content-Disposition', '%s' % self.contentDisposition)

        # start processing ranges
        length = None
        if meta[request.path].get('{DAV:}getcontentlength'):
            try:
                length = int(meta[request.path]['{DAV:}getcontentlength'])
            except:
                pass

        if length and request.env.get('HTTP_RANGE'):
            # process the range headers
            ranges = []
            try:
                ranges = parseRangeHeader(request.env['HTTP_RANGE'])
            except ValueError, ex:
                logging.getLogger().warn("Wrong Range Header: %s. Error was: %s" % \
                                        (request.env['HTTP_RANGE'], ex))

            if len(ranges) > 0:
                responseRanges = []
                total = 0
                for i, v in enumerate(ranges):
                    start = v[0]
                    end   = v[1]
                    start = int(start)
                    if end is not None:
                        end   = int(end)
                    else:
                        end = length-1

                    if end < start:
                        tmp = end
                        end = start
                        start = tmp
                    ranges[i] = (start,end)
                    total += end - start + 1
                    responseRanges.append("%s-%s/%s" % (start, end, length))
                request.setHeader('Content-Range','bytes %s' % ','.join(responseRanges))
                request.setResponseCode(206)
                length = total 

                # change the stream to be StreamRange(stream, ranges)
                stream = StreamRange(stream, ranges)

        if request.method == 'GET':
            if length is not None:
                request.setHeader('Content-Length', "%s" % length)
            request.write(stream)

        return meta

    def render_HEAD(self, request):
        return self.render_GET(request)


class GetPostResource(StaticResource):
    """
    Class that adds also the POST method support
    """
    def render_POST(self, request):
        if not request.env.has_key('CONTENT_TYPE'):
            request.setResponseCode(400)
            return

        user = request.env.get('user')
        try:
            isCollection = self.storageProvider.isCollection(request.path, user=user, cache=request.env['cache'])
        except OSError, e:
            request.setResponseCode(404)
            return

        meta = {}
        # process all meta data
        for (name, param) in request.params.items():
            meta[name] = param

        """
        if we post to a resource
            if the post contains files
                then the post must fail
            else
                the post attributes are added to the properties of the file
        else // we have a collection
            if there are files
                the files are created as resources in the collection
                and the other fields are added as attributes to the newly created
                resources, or the attributes are added only to the resource if the
                Depth header is 0
            else
                if the depth header is 0:
                    the attributes are assigned to the folder
                else:
                    all resources in the collection
        """
        affectedFiles = {}
        submittedFiles = len(request.files)
        try:
            if not isCollection:
                if submittedFiles > 0:
                    request.setResponseCode(409)
                    return
                else:
                    self.storageProvider.setMeta(request.path, meta, user=user, cache=request.env['cache'])
            else:
                if submittedFiles==0:
                    self.storageProvider.setMeta(request.path, meta, user=user, cache=request.env['cache'])

                if submittedFiles > 0:
                    path = request.path
                    if path[-1:] == '/':
                        path = path[:-1]
                    for name in request.files.keys():
                        files = request.files.getall(name)
                        for file in files:
                            fileName = "%s/%s" % (path,baseName(file.filename))
                            logging.getLogger().debug("Storing File: %s" % fileName)
                            try:
                                self.storageProvider.delete(fileName, user=user, cache=request.env['cache'])
                                self.storageProvider.delMeta(fileName, user=user, cache=request.env['cache'])
                            except:
                                pass
                            affectedFiles[fileName] = self.storageProvider.create(fileName, file, request.env, user=user, cache=request.env['cache'])
                            self.storageProvider.setMeta(fileName, meta, user=user, cache=request.env['cache'])
        except IOError, e:
            logging.getLogger().warn("@todo: Add error handling when creating file. Got error %s" % e)
            request.setResponseCode(409)
            return
                    
        request.setResponseCode(200)
        return affectedFiles

class WebdavResource(GetPostResource):
    lockProvider    = None
    notifier        = None

    def __init__(self, storageProvider, lockProvider, authProvider=None,
                 notifier=None, propertyACL=None, **kwargs):
        GetPostResource.__init__(self, storageProvider, authProvider, **kwargs)
        self.lockProvider    = lockProvider
        self.notifier        = notifier
        self.propertyACL     = propertyACL
        self.allowDirectoryListing = True

    def render(self, request):        
        if not (request.method == 'OPTIONS' and request.uri =='/'):
            affectedPaths = GetPostResource.render(self,request)
        else:
            affectedPaths = Resource.render(self, request)

        if affectedPaths and self.notifier and request.env.has_key('user'):
            for (path, meta) in affectedPaths.items():
                self.notifier.publish(
                                 user=request.env.get('user'),
                                 request=request,
                                 resource=self,
                                 path=path,
                                 meta=meta
                                 )

    def render_OPTIONS(self, request):
        request.setHeader('MS-Author-Via', 'DAV')
        request.setHeader('DAV', '1,2')
        request.setHeader('DAV', '<http://apache.org/dav/propset/fs/1>')
        request.setHeader('Allow', 'OPTIONS,GET,PUT,DELETE,MKCOL,PROPFIND,PROPPATCH')
        # The line below is only to make some webdav clients happy
        request.setHeader('Content-Type', 'httpd/unix-directory')
        request.setHeader('Content-Length', '0')

    def render_GET(self, request):
        """
        Get a resource data
        """
        try:
            if self.storageProvider.isCollection(request.path, user=request.env.get('user'), cache=request.env['cache']):
                request.env['HTTP_DEPTH'] = 1
                return self.render_PROPFIND(request)
        except IOError, e:
            if e.errno == 2:
                request.setResponseCode(404)
            else:
                request.setResponseCode(403)
            return

        return GetPostResource.render_GET(self,request)

    def render_POST(self, request):
        result = GetPostResource.render_POST(self, request)

        inputParams = {}
        if result is not None and len(result):
            inputParams = urlparse.parse_qs(request.query)
            
            if inputParams.has_key('_return'):
                if 'last' in inputParams['_return']:
                    request.path = result.keys().pop()
                    request.uri += '/'+ baseName(request.path)
                elif 'empty' in inputParams['_return']:
                    request.setResponseCode(200)
                    request.setHeader('Content-Type','text/html')
                    request.setHeader('Content-Length','0')
                    return result

        request.env['CONTENT_LENGTH'] = 0
        request.env['HTTP_DEPTH'] = 1
        self.render_PROPFIND(request)

        if inputParams.has_key('_callbackURL'):
            # Prevent header injection
            request.setHeader('Location', re.replace("[\n|\r]",'',inputParams['_callbackURL']))

        return result

    def render_PUT(self, request):
        logging.getLogger().debug("Started handling the request")
        #  read the data into chunks

        if self._isLocked(request):
            request.setResponseCode(423)
            return
            
        size = 0
        try:
            size = int(request.env['CONTENT_LENGTH'])
        except:
            logging.getLogger().debug('Invalid or missing Content-Length')
            pass

        # Special case for Mac OS X clients
        if request.env.has_key('HTTP_X_EXPECTED_ENTITY_LENGTH'):
            try:
                size = int(request.env['HTTP_X_EXPECTED_ENTITY_LENGTH'])
            except:
                pass

        user = request.env['user']
        if not user.hasQuota(size):
            # add JSON response when asked
            responseBody = ''
            if getResponseType(request) == 'json':
                responseBody = json.dumps({'message': 'Not enough quota'})
            else:
                responseBody = """<?xml version="1.0">
<error xmlns="DAV:">
    <quota-not-exceeded/>
</error>"""
            request.writeDirect(responseBody,507)
            return

        # first delete the resource
        """
        @todo: The overwrite is controlled by the If-Match and If-None-Match Headers
        """
        overwrite = False
        if request.env.has_key('HTTP_IF_MATCH'): # @todo: and the etag matches the existing etag
            overwrite = True

        difference = size
        try:
            meta = self.storageProvider.getMeta(request.path, user=user, cache=request.env['cache'])
            isCollection = meta[request.path].get('{DAV:}resourcetype', 0)
            isCollection = bool(isCollection)
            if isCollection == True:
                # A PUT request to an existing collection MAY be treated as an error (405 Method Not Allowed).
                # see: http://www.ietf.org/rfc/rfc4918.txt 9.7.2 PUT for Collections
                request.setResponseCode(405)
                return

            oldSize = int(meta[request.path]['{DAV:}getcontentlength'])
            difference -= oldSize
        except:
            pass

        if overwrite:
            try:
                # @todo: Or remove the view files ONLY
                self.storageProvider.delete(request.path, user=user, cache=request.env['cache'])
                self.storageProvider.delMeta(request.path, user=user, cache=request.env['cache'])
            except:
                logging.getLogger().error("Unable to delete old resource before overwriting")

        try:
            result = self.storageProvider.create(request.path, request, request.env, expectedSize=size, user=user, cache=request.env['cache'])
            request.env.get('user').changeQuota(-difference)
        except IOError, e:
            logging.getLogger().warn("@todo: Add error handling when creating file. Got error %s" % e)
            request.setResponseCode(409)
            return 

        # Mac OS X Special Case
        if request.env.has_key('HTTP_USER_AGENT') and \
        request.env['HTTP_USER_AGENT'].strip()[0:9]=='WebDAVFS/' and \
        request.env.has_key('HTTP_IF'):
            try:
                meta = self.storageProvider.getMeta(request.path, user=user, cache=request.env['cache'])
                request.setHeader('Content-Type', meta[request.path]['{DAV:}getcontenttype'])
                request.setResponseCode(204)
                return
            except:
                pass

        request.setHeader('Content-Type', 'text/html')                
        body = """<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>201 Created</title>
</head><body>
<h1>Created</h1>
<p>Resource %s has been created.</p>
<hr />
%s
</body></html>""" % (request.uri, '')
        request.writeDirect(body, 201)
        return {request.path: result}

    def render_PROPFIND(self, request):
        requestedProperties = {}
        tree = None

        try:
            tree = ET.parse(request);
        except:
            if request.env.has_key('CONTENT_LENGTH') and \
            int(request.env['CONTENT_LENGTH']) > 0:
                request.setResponseCode(400)
                return

        if tree is not None:            
            root = tree.getroot()

            allprop = root.find('./{DAV:}allprop')
            propname = root.find('./{DAV:}propname')

            if allprop and propname:
                """
                23.3.2.1  Example - XML Syntax Error

                The following request body for a PROPFIND method is illegal.

                <?xml version="1.0" encoding="utf-8" ?>
                   <D:propfind xmlns:D="DAV:">
                     <D:allprop/>
                     <D:propname/>
                </D:propfind>

                The definition of the propfind element only allows for the allprop or
                the propname element, not both.  Thus the above is an error and must
                be responded to with a 400 (Bad Request).
                """
                request.setResponseCode(400)
                return

            if allprop is not None:
                requestedProperties={}# get all visible properties
            elif propname is not None:
                requestedProperties[propname.tag]=1
            else:
                props = root.find('./{DAV:}prop')
                if not props:
                    request.setResponseCode(400)
                    return

                for prop in props:
                    requestedProperties[prop.tag] = 1

        logging.getLogger().debug("Requested Properties: %s" % requestedProperties)

        depth = 0
        if request.env.get('HTTP_DEPTH') and request.env['HTTP_DEPTH']!= '0':
            depth = 1

        try:
            meta   = self.storageProvider.getMeta(request.path, depth, requestedProperties, user=request.env.get('user'), cache=request.env['cache'])
        except (OSError, IOError), e:
            # Some User-Agents, like Konqueror want to have also response body
            request.writeDirect('<html><body><h1>Not Found</h1></body></html>', 404)
            logging.getLogger().error("render_PROPFIND(): got exception %s" % e)
            return

        # add the direct static children
        if depth != 0 and request.path == '/':
            path = request.path
            for (name, resource) in self.children.items():
                if not isinstance(resource, WebdavResource):
                    continue

                try:
                    resourceMeta = resource.storageProvider.getMeta(path, 0, requestedProperties, user=request.env.get('user'), cache=request.env['cache'])
                    meta[path+name] = resourceMeta[path]
                except:
                    meta[path+name] = {
                        '{DAV:}resourcetype': 1,
                        '{DAV:}getcontenttype': 'application/x-directory',
                        '{DAV:}displayname': name,
                        '{DAV:}getcontentlength': 0,
                        '{DAV:}getlastmodified': time.time()
                    }

        # add displayname property
        for (path, data) in meta.items():
            if data.has_key('{DAV:}displayname'):
                continue
            meta[path]['{DAV:}displayname'] = os.path.basename(path)
            if meta[path]['{DAV:}displayname'] == '':
                name = os.path.basename(request.uri)
                if name == '':
                    name = '/'
                meta[path]['{DAV:}displayname'] = name

            if self.propertyACL:
                # Filter keys that are not allowed for reading
                # according to the property ACL
                for key in data.keys():
                    if not self.propertyACL.isAllowed('read',key):
                        del meta[path][key]

        try:
            meta = self._filterProperties(meta, request)
        except Exception, ex:
            traceback.print_exc()
            logging.getLogger().error('render_PROPFIND(): _filterProperties threw: %s ' % ex)
            request.setResponseCode(400)
            return
        
        if self.lockProvider and \
        (requestedProperties.has_key('{DAV:}supportedlock') or not tree):
            meta[request.path]['{DAV:}supportedlock'] = self.lockProvider.getSupportedLocks(request.uri, user=request.env.get('user'))
            if depth!=0:
                for path, data in meta.items():
                    meta[path]['{DAV:}supportedlock'] = meta[request.path]['{DAV:}supportedlock']

        # add the quota information
        user = request.env.get('user')
        if user:
            try:
                if requestedProperties.has_key('{DAV:}quota-available-bytes'):
                    meta[request.path]['{DAV:}quota-available-bytes'] = user['quota_available']
                if requestedProperties.has_key('{DAV:}quota-used-bytes'):
                    meta[request.path]['{DAV:}quota-used-bytes'] = user['quota_total'] - user['quota_available']
            except KeyError:
                pass

        responseBody = ''
        postfix = request.uri
        if meta[request.path]['{DAV:}resourcetype'] and postfix[-1:] != '/':
            postfix += '/'
        
        if getResponseType(request) == 'json':
            request.setHeader('Content-Type', 'application/json; charset="utf-8"')
            jsonData = OrderedDict()
            for (path, data) in meta.items():
                href = path.replace(request.path, postfix,1)
                href = re.sub(r'/{2,}', '/', href)
                jsonData[href] = data
            responseBody = jsonData.toJson()
            if request.query.find('cb=')!=-1:
                try:
                    inputParams = urlparse.parse_qs(request.query)
                    if inputParams.has_key('cb'):
                        # we have JSONP request
                        responseBody = inputParams['cb'][0]+'('+responseBody+');'
                except ValueError:
                    pass
        else:
            request.setHeader('Content-Type', 'text/xml; charset="utf-8"')
            rootEl = createMutlipartResponse(request.path, meta, requestedProperties, postfix)
            responseBody = '<?xml version="1.0" encoding="utf-8" ?>' + "\n" + \
                           '<?xml-stylesheet type="text/xsl" href="/~static/propfind.xslt"?>' + "\n" +\
                          ET.tostring(rootEl, "utf-8")

        request.writeDirect(responseBody, 207)

    def render_PROPPATCH(self, request):
        if self._isLocked(request):
            request.setResponseCode(423)
            return

        try:
            tree = ET.parse(request);
            root = tree.getroot()
        except:
            request.setResponseCode(400)
            return

        allProps = {} # hash with property name and its status
        sets = root.findall('./{DAV:}set')
        if sets:
            for set in sets:
                props = set.findall('./{DAV:}prop')
                for prop in props:
                    for tag in prop:
                        if self.propertyACL and \
                        not self.propertyACL.isAllowed('write',tag.tag):
                            continue

                        allProps[tag.tag] = 0
                        try:
                            self.storageProvider.setMeta(request.path, {tag.tag: tag.text}, user=request.env.get('user'), cache=request.env['cache'])
                        except Exception, ex:
                            logging.getLogger().error("setMeta: Got Exception: %s" % ex)
                            allProps[tag.tag] = 1

        removes = root.findall('./{DAV:}remove')
        if removes:
            for remove in removes:
                props = remove.findall('./{DAV:}prop')
                for prop in props:
                    for tag in prop:
                        if self.propertyACL and \
                        not self.propertyACL.isAllowed('write',tag.tag):
                            continue

                        allProps[tag.tag] = 0
                        try:
                            self.storageProvider.delMeta(request.path, [tag.tag], user=request.env.get('user'), cache=request.env['cache'])
                        except:
                            allProps[tag.tag] = 1

        responseBody = ''
        if getResponseType(request) == 'json':
            logging.getLogger().warn("@todo: return the response as json")
            request.setHeader('Content-Type', 'application/json')
            responseBody = "%s" % allProps
        else:
            request.setHeader('Content-Type', 'text/xml')
            rootEl = ET.Element("{DAV:}multistatus")           
            responseEl = ET.SubElement(rootEl, '{DAV:}response')
            hrefEl = ET.SubElement(responseEl, '{DAV:}href')
            hrefEl.text = request.uri
            propstatEl = ET.SubElement(responseEl, '{DAV:}propstat')            
            for (propName, error) in allProps.items():
                propEl = ET.SubElement(propstatEl, '{DAV:}prop')
                ET.SubElement(propEl, propName)
                statEl = ET.SubElement(propstatEl, '{DAV:}status')
                if error:
                    statEl.text = "HTTP/1.1 409 Conflict"
                else:
                    statEl.text = "HTTP/1.1 200 OK"

            responseBody = '<?xml version="1.0" encoding="utf-8" ?>' + "\n" + \
                ET.tostring(rootEl, "utf-8")

        request.writeDirect(responseBody, 207)

        if len(allProps):
            return  {request.path: {'props': allProps}}

    def render_MKCOL(self, request):
        if self._isLocked(request):
            request.setResponseCode(423)
            return

        if request.env.has_key('CONTENT_LENGTH') and \
        long(request.env['CONTENT_LENGTH'].strip()) > 0:
            return request.setResponseCode(415)

        try:
            meta = self.storageProvider.getMeta(request.path, user=request.env.get('user'), cache=request.env['cache'])
            isCollection = meta[request.path].get('{DAV:}resourcetype', 0)
            isCollection = bool(isCollection)
            if isCollection == False:
                request.setResponseCode(409)
            else:
                request.setResponseCode(405)
            return
        except:
            pass


        try:
            self.storageProvider.createCollection(request.path, user=request.env.get('user'), cache=request.env['cache'])
        except EnvironmentError as e:
            logging.getLogger().warn("@todo: Handle delete exceptions from the storage provider %s" % e)
            if e.errno == storage.PRECONDITION_FAILED:
                request.setResponseCode(409)
            else:
                request.setResponseCode(405)
            return

        request.setResponseCode(201)
        return {request.path: {}}

    def render_DELETE(self, request):
        if self._isLocked(request):
            request.setResponseCode(423)
            return

        meta = { request.path: {}}
        try:
            meta = self.storageProvider.getMeta(request.path, user=request.env.get('user'), cache=request.env['cache'])
            request.setHeader('Content-Type', meta[request.path]['{DAV:}getcontenttype'].encode('ascii'))
        except EnvironmentError as e:
            if e.errno == storage.NOT_FOUND:
                request.setResponseCode(404)
                return
        except:
            pass
        
        try:
            availableBytes = self.storageProvider.getSize(request.path, -1, user=request.env.get('user'), cache=request.env['cache'])
            self.storageProvider.delete(request.path, user=request.env.get('user'), cache=request.env['cache'])
            self.storageProvider.delMeta(request.path, user=request.env.get('user'), cache=request.env['cache'])
        except (OSError, IOError) as e:
            logging.getLogger().warn("@todo: Handle delete exceptions from the storage provider %s. Stack Trace: %s" % (e,traceback.format_exc()))
            if e.errno == 2:
                request.setResponseCode(404)
            else:
                request.setResponseCode(409)
            return

        # return the bytes back to the quota
        request.env.get('user').changeQuota(availableBytes)

        request.setResponseCode(204)

        return meta

    def render_LOCK(self, request):
        root = None
        try:
            tree = ET.parse(request);
            root = tree.getroot()
        except:
            if request.env.has_key('CONTENT_LENGTH') and \
            int(request.env['CONTENT_LENGTH']) > 0:
                logging.getLogger().error('render_LOCK: Got Content-Length(%s) > 0' % request.env['CONTENT_LENGTH'])
                request.setResponseCode(400)
            return

        timeout = None
        if request.env.has_key('HTTP_TIMEOUT'):
            timeout = self._parseTimeoutHeader(request.env['HTTP_TIMEOUT'])

        if not root:
            """
            A client may submit a LOCK method with an If header but
            without a body.  This form of LOCK MUST only be used to "refresh" a
            lock.  Meaning, at minimum, that any timers associated with the lock
            MUST be re-set.
            """
            if not request.env.has_key('HTTP_IF'):
                request.setResponseCode(400)
                return

            # get the token from the if header
            token = self._parseIfHeader(request.env['HTTP_IF'])

            try:
                self.locking.refresh(request.uri, token, timeout)
                request.setResponseCode(423)
            except:
                # if there is an error refreshing the token, this means that this
                # token is no longer valid
                request.setResponseCode(412)

            return

        if self._isLocked(request):
            request.setResponseCode(423)
            return

        scope = SCOPE_SHARED
        lockscope = root.find('./{DAV:}lockscope')
        if lockscope:
            if lockscope.find('{DAV:}exclusive') is not None:                
                scope = SCOPE_EXCLUSIVE

        type = TYPE_READ
        locktype  = root.find('./{DAV:}locktype')
        if locktype:            
            if locktype.find('{DAV:}write') is not None:
                type = TYPE_WRITE

        owner = None
        ownerEl = root.find('./{DAV:}owner')
        if ownerEl:
            hrefEl = ownerEl.find('{DAV:}href')
            if hrefEl is not None:
                owner = hrefEl.text
            
        """
           Check if the resource was already locked and if yes
           use the table below to figure out if it can be locked again 
        
           Current lock state/  |   Shared Lock   |   Exclusive
           Lock request         |                 |   Lock
           =====================+=================+==============
           None                 |   True          |   True
           ---------------------+-----------------+--------------
           Shared Lock          |   True          |   False
           ---------------------+-----------------+--------------
           Exclusive Lock       |   False         |   False*
           ------------------------------------------------------
        """

        # assemble the final result
        
        # @todo: Add later support for multi-locks
        #        Locking a collection with depth > 0 makes multi lock
        # @see: http://www.ietf.org/rfc/rfc2518.txt 8.10.10 Example - Multi-Resource Lock Request
        try:
            token = self.lockProvider.lock(request.uri, timeout, owner, type, scope, user=request.env.get('user'))
        except ValueError, ex:
            logging.getLogger().error('Unable to lock %s. Got exception: %s' % (request.uri, ex))
            request.setResponseCode(423)
            return


        locks = {
            request.uri: {
                'locktype' : type,
                'lockscope': scope,
                'depth'    : 0, # 'number|infinity',
                'timeout'  : 'Second-3600',
                'locktoken': 'opaquelocktoken:%s' % token,
                'status'   : '200' # HTTP status code 
            }
        }

        responseType = getResponseType(request)

        responseBody = ''
        responseCode = 200
        if responseType == 'json':
            request.setHeader('Content-Type', 'application/json')
            jsonData = {}
            for (href, data) in locks.items():
                # @todo: make other operations
                jsonData[href] = data
            responseBody = json.dumps(jsonData, sort_keys=True)
        elif len(locks)==1:
            request.setHeader('Content-Type', 'text/xml')
            request.setHeader('Lock-Token', '<opaquelocktoken:%s>' % token)                       
            
            rootEl = ET.Element("{DAV:}prop")
            lockEl = ET.SubElement(rootEl, '{DAV:}lockdiscovery')
            propEl = ET.SubElement(lockEl, '{DAV:}activelock')
            for (href, data) in locks.items():                
                for (name,value) in data.items():
                    if name == 'status':
                        continue
                        
                    currentEl = ET.SubElement(propEl, '{DAV:}'+name)
                    if name == 'lockscope':
                        if value == SCOPE_EXCLUSIVE:
                            ET.SubElement(currentEl, '{DAV:}exclusive')
                        else:
                            ET.SubElement(currentEl, '{DAV:}shared')
                    elif name == 'locktype':
                        if value == TYPE_READ:
                            ET.SubElement(currentEl, '{DAV:}read')
                        else:
                            ET.SubElement(currentEl, '{DAV:}write')
                    elif name == 'locktoken':
                        hrefEl = ET.SubElement(currentEl, '{DAV:}href')
                        hrefEl.text = value
                    elif name == 'owner':
                        hrefEl = ET.SubElement(currentEl, '{DAV:}href')
                        hrefEl.text = value
                    else:                        
                        currentEl.text = "%s" % value

            responseBody = '<?xml version="1.0" encoding="utf-8" ?>' + "\n" + \
                            ET.tostring(rootEl, "utf-8")
                            
        elif len(locks) > 1:
            request.setHeader('Content-Type', 'text/xml')
            
            # @todo: Implent this later
            """
            <?xml version="1.0" encoding="utf-8" ?>
   <D:multistatus xmlns:D="DAV:">
     <D:response>
          <D:href>http://webdav.sb.aol.com/webdav/secret</D:href>
          <D:status>HTTP/1.1 403 Forbidden</D:status>
     </D:response>
     <D:response>
          <D:href>http://webdav.sb.aol.com/webdav/</D:href>
          <D:propstat>
               <D:prop><D:lockdiscovery/></D:prop>
               <D:status>HTTP/1.1 424 Failed Dependency</D:status>
          </D:propstat>
     </D:response>
   </D:multistatus>
   """

            responseCode = 207
            rootEl = ET.Element("{DAV:}multistatus")

            for (href, data) in locks.items():
                responseEl = ET.SubElement(rootEl,'{DAV:}response')
                hrefEl     = ET.SubElement(responseEl,'{DAV:}href')
                hrefEl.text = href

                statEl     = ET.SubElement(responseEl,'{DAV:}status')
                # @todo: Fix the line below
                statEl.text = 'HTTP/1.1 %s %' % (data.status, 'Message')

                if data.status == 200:
                    lockEl = ET.SubElement(responseEl, '{DAV:}lockdiscovery')
                    propEl = ET.SubElement(lockEl, '{DAV:}activelock')
                    for (href, data) in locks.items():
                        for (name,value) in data.items():
                            tmpEl = ET.SubElement(propEl, name)
                            tmpEl.text = value

        request.writeDirect(responseBody, responseCode)
        

    def render_UNLOCK(self, request):        
        if not request.env.has_key('HTTP_LOCK_TOKEN'):
            request.setResponseCode(400)
            return
        
        m = re.match('<opaquelocktoken:(.*?)>', request.env['HTTP_LOCK_TOKEN'].strip())
        if m is None:
            request.setResponseCode(423)
            return

        token = m.groups(0)[0].strip()
        
        try:
            self.lockProvider.unlock(request.uri,token, user=request.env.get('user'))
        except:
            # the token is invalid for this uri
            request.setResponseCode(423)
            return

        # Mac OS X Special Case
        if request.env.has_key('HTTP_USER_AGENT') and \
        request.env['HTTP_USER_AGENT'].strip()[0:9]=='WebDAVFS/':
            try:
                meta = self.storageProvider.getMeta(request.path, user=request.env.get('user'), cache=request.env['cache'])
                request.setHeader('Content-Type', meta[request.path]['{DAV:}getcontenttype'])
            except:
                pass

        request.setResponseCode(204)

    def render_COPY(self, request):
        def callback(sourceUri, destResource, destPath, depth):
            logging.getLogger().debug("Executing Copy: %s %s" % (sourceUri, destPath))
            self.storageProvider.copy(sourceUri, destPath, depth, user=request.env.get('user'), cache=request.env['cache'])

            meta = self.storageProvider.getMeta(sourceUri, None, depth, user=request.env.get('user'), cache=request.env['cache'])
            for path, data in meta.items():
                path = path.replace(sourceUri, destPath)
                destResource.storageProvider.setMeta(path, data, depth, user=request.env.get('user'), cache=request.env['cache'])

            size = self.storageProvider.getSize(sourceUri, depth, user=request.env.get('user'), cache=request.env['cache'])
            request.env.get('user').changeQuota(size)

        return self._handleCopyMove(request, callback)

    def render_MOVE(self, request):

        def callback(sourceUri, destResource, destPath, depth):
            self.storageProvider.move(sourceUri, destPath, depth, user=request.env.get('user'), cache=request.env['cache'])

        return self._handleCopyMove(request, callback)

    def _handleCopyMove(self, request, call):
        logging.getLogger().warn("Request env: %s" % request.env)

        if not request.env.get('HTTP_DESTINATION'):
            # copy MUST have destination header
            request.setResponseCode(400)
            return

        destinationUri = request.env['HTTP_DESTINATION']
        if destinationUri != '/':
            destinationUri = urlparse.urlparse(destinationUri)[2]
        destinationUri = normalizeUri(destinationUri)
        (sourceParent, _) = os.path.split(request.uri)
        if destinationUri == "":
            destinationUri = '/'
        if request.uri == destinationUri or\
        sourceParent == destinationUri:
            request.setResponseCode(403)
            return

        logging.getLogger().warn("""@todo:
            - Check if the target resource can be read (current resource)
            - Check if the destination resource allows to copy objects to it
            - etc.
        """)
        
        [destResource, destPath ] = Resolver.getResourcePathForUri(destinationUri, request.env['VHOST']['root'])

        logging.getLogger().debug("_handleCopyMove: From %s to %s" % (request.path, destPath))

        if destResource.lockProvider.getLocks(destinationUri, user=request.env.get('user')):
            request.setResponseCode(423)
            return

        targetExists = False
        if request.env.get('HTTP_OVERWRITE') and destResource.storageProvider.exists(destPath, user=request.env.get('user'), cache=request.env['cache']):
            """
            If a resource exists at the destination and the Overwrite header is
            "T" then prior to performing the move the server MUST perform a
            DELETE with "Depth: infinity" on the destination resource.  If the
            Overwrite header is set to "F" then the operation will fail.
            """
            targetExists = True
            if request.env['HTTP_OVERWRITE'].strip().upper() == 'F':
                # check if the target storage exists - if yes
                # - do not allow it to overwrite
                request.setResponseCode(412)
                return
            elif request.env['HTTP_OVERWRITE'].strip().upper() == 'T':
                try:
                    destResource.storageProvider.delete(destPath, user=request.env.get('user'), cache=request.env['cache'])
                except OSError, e:
                    # suppress any warnings at this stage
                    pass
            pass

        depth = 0
        if request.env.get('HTTP_DEPTH'):
            depth = request.env['HTTP_DEPTH']
            if depth.lower() == 'infinity':
                depth = -1
            try:
                depth = int(depth)
            except ValueError:
                depth = 0

        if not isinstance(destResource, WebdavResource):
            logging.getLogger().warn("@todo: we do not know how to handle copying to other resources")
            request.setResponseCode(502)
            return

        try:
            call(request.path, destResource, destPath, depth)
        except IOError, e:
            request.setResponseCode(409)
            logging.getLogger().warn("_handleCopyMove(): Got exception: %s" % e)
            return

        if targetExists:
            request.setResponseCode(204)
        else:
            request.setResponseCode(201)

        return {request.path: {'destination': destPath}}


    

    def _isLocked(self, request):
        """
        Checks if a resource is locked and if the if-header
        matches some of the unlock conditions
        """

        token = None
        if request.env.has_key('HTTP_IF'):
            token = self._parseIfHeader(request.env['HTTP_IF'])

        locks = self.lockProvider.getLocks(request.uri, user=request.env.get('user'))
        if locks is None:
            return False

        if token:
            try:
                del locks[token]
            except:
                pass

        if len(locks):
            return True
        else:
            return False

    def _parseTimeoutHeader(self, header):
        validTimeout = None
        timeouts = header.split(',')
        for timeout in timeouts:
            timeout = timeout.strip().lower()
            if timeout.find('second-') == 0:
                validTimeout = timeout.split('-')[1]
                validTimeout = validTimeout.strip()
                break
        return validTimeout

    def _parseIfHeader(self, header):
        """
        Return list of uris and tokens for them
        """
        token = None

        m = re.search("\(<(.*?)>\)",header)
        if m:
            token = m.groups(0)[0]
            ns = 'opaquelocktoken:'
            if token.find(ns) == 0:
               token = token[len(ns):]

        return token

    def _filterProperties(self, meta, request, removeRoot=False):
        """
        Method that filters the properties.
        For example: /folder/?_limit=1,2&_sort=field,order&_filter[name]=value
        """
        if request.query == '':
            # nothing to change
            return meta;
        
        inputParams = urlparse.parse_qs(request.query)

        rootMeta = {}
        if removeRoot==False:
            rootMeta = meta[request.path]
        
        # get filters, if any
        filters = {}
        for (key, value) in inputParams.items():
            g = re.match('_filter\[(.*?)\]', key)
            if g is not None:
                name = g.group(1)
                filters[name] = value[0]

        if len(filters) > 0:            
            for(path, data) in meta.items():
                for (key, value) in filters.items():
                    text = data.get(key)
                    if text is None:
                        del meta[path]
                        continue

                    text = "%s" % text
                    if text.find(value)!=0:
                        del meta[path]        

        if inputParams.has_key('_sort') or inputParams.has_key('_limit'):
            orderedMeta = OrderedDict(meta)

            if inputParams.has_key('_sort'):
                (field, order) = inputParams['_sort'][0].split(',')

                def lowerCase(value):
                    return value.lower()

                castMap = {
                    '{DAV:}getcontentlength': long,
                    '{DAV:}getlastmodified' : float,
                    '{DAV:}displayname' : lowerCase
                }

                orderedMeta.sort(field, order.lower()=='asc',
                                 castMap.get(field,None)
                                 )

            if inputParams.has_key('_limit'):
                (offset, length) = inputParams['_limit'][0].split(',')
                offset = int(offset)
                length = int(length)
                max    = offset + length

                orderedMeta = orderedMeta[offset:max]

            meta = orderedMeta

        if not meta.has_key(request.path) and removeRoot==False:
            meta[request.path]=rootMeta
        
        return meta

    @classmethod
    def __instancecheck__(cls, instance):
        if instance.__class__ == WebdavResource or \
        issubclass(instance.__class__, WebdavResource) or \
        isinstance(instance, LimitedResourceDecorator):
            return True
        return False
            

class ProxyResource(Resource):
    
    def __init__(self, url):
        Resource.__init__(self)
        self.url = url

    def getChild(self, path, request):        
        return ProxyResource(self.url + '/' + urlquote(path, safe=""))

    def render_GET(self, request):
        headers = {}
        headers['Connection'] = 'Keep-Alive'
        if request.env.has_key('HTTP_USER_AGENT'):
            headers['User-Agent'] = request.env['HTTP_USER_AGENT']
        if request.env.has_key('HTTP_COOKIE'):
            headers['Cookie'] = ', '.join(request.env['HTTP_COOKIE'])

        logging.getLogger().debug("ProxyGET: URL: %s" % self.url)

        if request.query:
            self.url += '?' + request.query

        urlRequest = Request(self.url, None, headers)
        try:
            f  = urlopen(urlRequest)
        except HTTPError, e:            
            request.setResponseCode(e.code)
            request.finish()
            logging.getLogger().warn('Not Found: %s ' % e.code)
            return

        request.setResponseCode(200)

        def generator():
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                yield chunk

        request.write(generator)
        request.finish()

from core.pattern import Decorator
class LimitedResourceDecorator(Decorator):
    """
    Resource decorator that limits the methods that can be called
    to the ones listed in the allowedMethods
    """

    def __init__(self, obj, allowedMethods):
        Decorator.__init__(self, obj)
        object.__setattr__(self, "allowedMethods", allowedMethods)

    def render(self, request):
        if not (request.method in self.allowedMethods):
            request.setResponseCode(405)
            return

        return self._obj.render(request)

class TokenResource(Resource):
    tree  = None
    authProvider = None

    def __init__(self, tree, authProvider):
        Resource.__init__(self)
        self.tree  = tree
        self.authProvider  = authProvider

    def render(self, request):
        # Nothing to be rendered here
        # This method is needed if the authentication fails
        return

    def getChild(self, path, request):
        #if request.method == 'OPTIONS':
        #    return self.tree

        try:
            if request.prepath[0][0] == '~':
                return self.tree.getChildWithDefault(path, request)
        except IndexError:
            pass

        if not self.authProvider.authenticate(request):
            request.postpath = []
            return self
        
        if not request.env.has_key('user'):
            # create the webdav user object
            request.env['user'] = self.authProvider.getUser(request)

        return self.tree

class TokenWebdavResource(WebdavResource):
    """
    Resource that adds limitations based on the access token.
    The limitations can be
        max-file-count - total number of files in a directory
        max-file-size - max size in bytes per file
        max-total-size - max size of all files in a directory
        mime-types - list of allowed mime types
                image/ - for all images or
                image/png for PNG images only
        auth - dict with username:encrypted-password
    """


    def _loadAccessRules(self, request):

        if request.env.has_key('auth') and request.env['auth'].has_key('settings'):
            return request.env['auth']['settings']

        request.env['auth']['settings'] = {}
        """
        public env['auth']['settings'] = { // Settings taken from a file for a shared, token protected directory.
		'mime-types': [<allowed-mime-types>],
		'auth': ['<one line with digest authentication>',...],
		'max-file-size': upload limit in bytes per file
	}
        """
        try:
            stream = self.storageProvider.get("%s/.%s.axs" % (request.env['auth']['path'], request.env['auth']['checksum']), user=request.env.get('user'), cache=request.env['cache'])
        except:
            return {}

        try:
            request.env['auth']['settings'] = json.load(stream)
        except:
            logging.getLogger().error('Invalid access file')
            return {}

        logging.getLogger().debug('Loaded Axs file')

        return request.env['auth']['settings']

    def _checkMimeTypes(self, request, mimeType):
        if request.env['auth']['settings'].has_key('mime-types'):
            allowed = False
            for allowedMime in request.env['auth']['settings']['mime-types']:
                if mimeType.startswith(allowedMime):
                    allowed = True
                    break

            if not allowed:
                raise Exception('Not allowed mime type')

    def _checkAuth(self, request):
        if request.env['auth']['settings'].has_key('auth'):
            import core.provider.authentication as auth
            import conf.server as serverConf
            authProvider = auth.DigestAuthProvider(
                                        serverConf.Config['user_realm'],
                                        request.env['auth']['settings']['auth'],
                                        False
                                                  )
            if not authProvider.authenticate(request):
                return False
            request.env['auth']['user'] = authProvider.getIdentity(request)
        return True


    def _checkMaxFileSize(self, request, size):
        if request.env['auth']['settings'].has_key('max-file-size'):
            if size > int(request.env['auth']['settings']['max-file-size']):
                raise Exception('File is bigger than allowed')

    def _isAxs(self, request):
        if request.path.endswith("%s/.%s.axs" % (request.env['auth']['path'], request.env['auth']['checksum'])):
            # deny read access to the axs files
            request.setResponseCode(403)
            return True

        return False

    def render(self, request):
        self._loadAccessRules(request)
        return WebdavResource.render(self, request)


    def render_GET(self, request):
        if self._checkAuth(request):
           return WebdavResource.render_GET(self, request)

    def render_PUT(self, request):
        """
        Put command that is respecting the auth settings
        """
        if self._isAxs(request):
            # deny write access to the axs files
            return

        if not len(request.env['auth']['settings']):
            return WebdavResource.render_PUT(self, request)

        # Pre: Make initial limitation based on the request headers
        try:
            self._checkMimeTypes(request, request.env['CONTENT_TYPE'])
            self._checkMaxFileSize(request, int(request.env['CONTENT-LENGTH']))
        except Exception, ex:
            logging.getLogger().error('Precondition failed: %s' % ex)
            request.setResponseCode(412)
            return

        result = WebdavResource.render_PUT(self, request)

        # Post: make checks after the file is uploaded
        try:
            meta = self.storageProvider.getMeta(request.path, 0, user=request.env.get('user'), cache=request.env['cache'])
            meta[request.path]['{DAV:}getcontentlength']
            meta[request.path]['{DAV:}getcontenttype']

        except Exception, ex:
            logging.getLogger().error('Unable to load the newly created file')
            return result

        try:
            self._checkMimeTypes(request, meta[request.path]['{DAV:}getcontenttype'])
            self._checkMaxFileSize(request, int(meta[request.path]['{DAV:}getcontentlength']))
        except Exception, ex:
            logging.getLogger().error('Precondition failed: %s' % ex)
            request.setResponseCode(412)
            return

        return result

    def render_POST(self, request):
        fileCount = 0
        for (name, param) in request.params.items():
            if hastattr(param,'filename'):
                fileCount+=1
                if name == ".%s.axs" % (request.env['auth']['path'], request.env['auth']['checksum']):
                    logging.getLogger().error('Attempt to overwrite the axs file')
                    request.setResponseCode(403)
                    return
                # @todo: check Mime Types + check File Size

        return WebdavResource.render_POST(self, request)
