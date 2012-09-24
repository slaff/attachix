# To change this template, choose Tools | Templates
# and open the template in the editor.
import ujson as json
import logging
import time

from core.pool.Redis import ConnectionPool

class Event():
    timeout = 7200 # 2 minutes
    
    def subscribe(self, channel, lastId=None):
        queue = ConnectionPool().getConnection()
        if not lastId:
            lastId = time.time() - self.timeout

        # remove stale messages in the archive
        queue.zremrangebyscore(channel,'-inf','%s' % lastId)

        # then get usable messages that are in the archive
        events = queue.zrangebyscore(channel, '(%s' % (float(lastId)+0.0001), '+inf')
        # @todo:
        # 	Implement compaction here
        # 	- reverse the list
        # 	- if there is newer event about a resource - ignore all the old
        # 	  for this event

        for event in events:
            yield event

        pubsub = queue.pubsub()
        pubsub.subscribe(channel)
        for event in pubsub.listen():
            logging.getLogger().debug('Event:Subscribe() Got event: %s' % event)
            if event['type'] != 'message':
                continue
            yield event['data']
        pubsub.unsubscribe(channel)
        
    def publish(self, channel, data, timestamp=None):
        if not timestamp:
            timestamp = time.time()
        queue = ConnectionPool().getConnection()
        logging.getLogger().debug('Event:publish(%s): %s ' % (channel, data))
        message = json.dumps(data)
        queue.publish(channel, message)
        queue.zadd(channel, timestamp, message)
        queue.expire(channel, self.timeout)