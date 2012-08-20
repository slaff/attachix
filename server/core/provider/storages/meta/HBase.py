# -*- coding: utf-8 -*-

import re
import logging

from core.provider.data.HBase import ActiveRecord

class Nodes(ActiveRecord):
    pass

class Paths(ActiveRecord):
    pass

class Entry():
    path = None
    node = None
    
    def __init__(self, client=None):
        self.path = Paths(client)
        self.node = Nodes(client)

    def find(self, row):
        """
        Tries to find existing entry based on the row key
        @param string row
        """
        if not self.path.find(row):
            raise KeyError("No row for this key was found")
        self.node.find(self.path['id'])

    def save(self):
        self.node.save()
        self.path.save()

from core.pool.HBase import ConnectionPool
from threading import local
class Meta(local):
    """
    Class for fast discovery of nodes

    @todo: implement some caching here
    """
    client = None

    def __init__(self):
        self.client = ConnectionPool().getConnection()
    
    def findByPath(self, path, depth=0):
        """
        Finds nodes matching the url path
        @param string path, example '00..01-/this/folder/-file'
        @param int depth 

        @return
                None if not found
                {Entry} if depth = 0
                list of {Entry} if depth > 0
        """
        entries = []
        if depth == 0:
            entry = Entry(self.client)
            try:
                entry.find(path)
            except Exception, ex:
                print "findByPath:", ex
                return None
            return entry

        bits = path.split(':')
        if depth == 1:
            # find direct children
            startRow = "%s:%s%s/:" % (bits[0],bits[1],bits[2])
        else: # depth infinity
            # find all children
            startRow = "%s:%s%s/" % (bits[0],bits[1],bits[2])
        startRow = re.sub(r'/{2,}', '/', startRow)
        stopRow  = startRow + "я"

        logging.getLogger().debug("Start: %s, Stop: %s" % (startRow, stopRow))
        scanner = self.client.scannerOpenWithStop('paths', startRow, stopRow, ['id'])
        while True:
            results  = self.client.scannerGet(scanner)
            if not results:
                break

            result = results[0]
            entry = Entry(self.client)
            try:
                entry.find(result.row)
            except:
                continue
            entries.append(entry)

        return entries

    def new(self):
        return Entry(self.client)
