import traceback
import logging
import os
import os.path
import urllib

from amqplib import client_0_8 as amqp
import conf.server
import core.coder as coder
from core.models.Hypertable import Conversions
from core.notify.plugins import base
import core.utils as utils
from conf.vhosts.available.token import VHost as TokenVHost
import ujson as json
import traceback

from core.pool.RabbitMQ import ConnectionPool

class Plugin(base.Plugin):
    subscribe = ['PUT','POST']

    name    = 'JobClient'
    description = 'RabbitMQ JobClient notification plugin'
    author  = 'Slavey Karadzhov <slaff@linux-bg.org>'
    version = '0.1'

    """
    @param int user
    @param Request request
    @param Resource resource
    @param string event
    @param string uri  - the path in the global resource tree
    @param string path - the local resource path
    @param array meta
    """
    def process(self, user, request, resource, path, meta):
        # the smalles JPEG image is 134 bytes
        # @see: http://stackoverflow.com/questions/2253404/what-is-the-smallest-valid-jpeg-file-size-in-bytes

        if not meta:
            meta = resource.storageProvider.getMeta(path, user=user)
            meta = meta[path]

        # don't bother the conversion queue for items that are smaller than minSize bytes
        size = None
        try:
            size = int(meta['{DAV:}getcontentlength'])
            if size < conf.server.Config['jobclient']['minSize']:
                return
        except Exception as ex:
            logging.getLogger().warn("Incorrect job client configuration: %s" % ex)

        # Step 0: Deduplicate the data, if the storage provider supports it
        minDeduplicationSize = 0
        try:
            minDeduplicationSize = conf.server.Config['jobclient']['minDedupSize']
        except Exception as ex:
            logging.getLogger().warn("Incorrect job client configuration: %s" % ex)

        if size and size > minDeduplicationSize:
            try:
                deduplicate = getattr(resource.storageProvider, 'deduplicate')
                if deduplicate(path, user=user):
                    try:
                        addCache = getattr(resource.storageProvider, 'addCache')
                        # if we use cache decorator -> then refresh the cache for this item
                        addCache(path, user=user)
                    except:
                        pass
                    # This is already processed item -> do not run the conversion for it.
                    return
            except Exception as ex:
                logging.getLogger().warn('Deduplicaiton failed: %s, Exception: %s' % (ex, traceback.format_exc()))
        
        connection = ConnectionPool().get().getConnection()
                               
        channel = connection.channel()
        channel.basic_qos(0,1,False)
        """
        Before we start figure out the exact mime type of the file
        and some additional properties
        """
        localPath = resource.storageProvider._translateUri(path, user=user)

        # Step 1: Figure out the mime type
        mediaInfo = utils.mediaInfo(localPath)

        mimeType = None
        if mediaInfo.has_key('General') and mediaInfo['General'].has_key('InternetMediaType'):
            mimeType = mediaInfo['General']['InternetMediaType']
            resource.storageProvider.setMeta(path, {'{DAV:}getcontenttype': mimeType}, user=user)
        else:
            [mimeType, encoding] = utils.getMime(localPath)

        if not mimeType:
            return
        
        # Step 2: For the current user, his/hers conversion group,  path and mime-major get the conversions
        #         that can be applied
        userId = user.get('id')
        dir    =  os.path.dirname(path)
        conversionGroup = user.get('caps:conversion_group') # the convertion group is the default convertions that the user has
        (major, minor) = mimeType.split('/',1)

        converter   = Conversions()
        allConversions = { '*': [], major: []}
        if conversionGroup:
            groupAllConversions = converter.findRange(
                            "%s-%s-%s" % (conversionGroup, '*', '/'),
                            "%s-%s-%s" % (conversionGroup, '*',dir),
                              )

            groupMimeConversions = converter.findRange(
                            "%s-%s-%s" % (conversionGroup, major, '/'),
                            "%s-%s-%s" % (conversionGroup, major, dir),
                              )

            allConversions = {
                '*'   : groupAllConversions,
                major : groupMimeConversions
            }
        
        
        userAllConversions = converter.findRange(
                            "%s-%s-%s" % (userId, '*', '/'),
                            "%s-%s-%s" % (userId, '*', dir),
                              )

        userMimeConversions = converter.findRange(
                            "%s-%s-%s" % (userId, major, '/'),
                            "%s-%s-%s" % (userId, major, dir),
                              )
       
        allConversions['*']   += userAllConversions
        allConversions[major] += userMimeConversions

        cipher = coder.SecureLink(**conf.server.Config['secret'])
        resourceUri = path.replace(request.path,request.uri)
        tokenServer = 'http://'+TokenVHost.host[0]+':'+TokenVHost.port+'/'
        tokenUrl = tokenServer + urllib.quote(cipher.encode(['GET','PROPPATCH'], user.getIdentity(), resourceUri))

        [viewLocalFolder, viewBaseURL] = resource.storageProvider.getView(path, request, user=user)
        # create the local base folder where the data will be stored
        if viewLocalFolder and not os.path.exists(viewLocalFolder):
            logging.getLogger().debug("Create new view Local Folder: %s" % viewLocalFolder)
            os.makedirs(viewLocalFolder)

        jobs = {}
        for key, convertions in allConversions.items():
            for conversion in convertions:
                actions = {}
                for (name, value) in conversion.items():
                    try:
                        if name.find('action:') != -1:
                            action = name[len('action:'):]

                            accepted = conversion.get('accept:'+action)
                            if accepted:
                                accepted = json.loads(accepted)
                                if not minor in accepted:
                                    continue

                            actions[action] = json.loads(value)
                    except:
                        logging.getLogger().error('Conversion data is wrong: %s' % traceback.format_exc())
                        continue

                for name, options in actions.items():
                    routingKey = "%s.%s" % (key, name)
                    if not jobs.has_key(routingKey):
                        jobs[routingKey] = {
                            'url': tokenUrl,
                            'source': localPath,
                            'meta' : meta,
                            'mime' : mimeType,
                            'targetFolder': viewLocalFolder,
                            'targetBaseURL': viewBaseURL,
                            'options': {}
                        }

                    jobs[routingKey]['options'].update(options)



        for routingKey, job in jobs.items():
            logging.getLogger().debug("Sending: RoutingKey:[%s], Message:[%s]" % (routingKey, json.dumps(job)))
            msg = amqp.Message(json.dumps(job))
            msg.properties["delivery_mode"] = 2
            channel.basic_publish(msg,
                    exchange='workers',
                    routing_key=routingKey
            )

        channel.close()