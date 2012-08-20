# -*- coding: utf-8 -*-
import time
import logging
import re
import traceback

from core.provider.data.Hypertable import ActiveRecord

from hyperthrift.gen.ttypes import RowInterval
from hyperthrift.gen.ttypes import ScanSpec

class Nodes(ActiveRecord):
    pass

class Paths(ActiveRecord):
    pass

class Entry():
    path = None
    node = None

    def __init__(self):
        self.path = Paths()
        self.node = Nodes()

    def find(self, row):
        """
        Tries to find existing entry based on the row key
        @param string row
        """
        if not self.path.find(row):
            raise KeyError("No row for this key was found")
        if self.path.has_key('id'):
            self.node.find(self.path['id'])

    def save(self):
        if self.path.has_key('id'):
            self.node.save()
        self.path.save()

class LightRow():
    row = None
    data = {}

    def __init__(self):
        self.data = {}
        self.row  = None

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, defaultValue=None):
        return self.data.get(key, defaultValue)

    def has_key(self, key):
        return self.data.has_key(key)

    def items(self):
        return self.data.items()

class LightEntry():
    path = None
    node = None

    def __init__(self):
        self.path = LightRow()
        self.node = LightRow()
    
from core.pool.Hypertable import ConnectionPool
from threading import local
class Meta(local):
    """
    Class for fast discovery of nodes

    @todo: implement some caching here
    """
    connectionWrapper = None

    def __init__(self):
        self.connectionWrapper = None

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
            entry = Entry()
            try:
                entry.find(path)
            except Exception, ex:
                logging.getLogger().debug("findByPath (%s): %s" % (path, traceback.format_exc()) )
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
        start = time.time()
        (client, namespace) = self._getClientNamespace()
        if depth == 0:
            scanner = client.scanner_open(namespace, "paths",
                   ScanSpec(
                            row_intervals=[RowInterval(
                                start_row=startRow,
                                end_row=stopRow
                            )],
                            return_deletes=False,
                            # revs=1,
                            columns=['id']),
                  )

            results = client.scanner_get_cells_as_arrays(scanner)
            client.scanner_close(scanner)
            logging.getLogger().debug('Scan hypertable: %s' % (time.time() - start))

            start = time.time()
            for result in results:
                entry = Entry(client, namespace)
                try:
                    entry.find(result[0])
                except:
                    continue

                entries.append(entry)
            logging.getLogger().debug('Finding entries: %s' % (time.time() - start))
        else:
            """
            The implementation in the if does not scale well if there are a lot of entries in the result set.
            Therefore we use this "light" version.
            """
            s = client.hql_exec(namespace,
                                      "SELECT * FROM paths WHERE  '%s' <= ROW < '%s' REVS 1" % (startRow, stopRow), 0, 1)
            # gather the ids of the nodes....
            scanner = s.scanner
            results = client.scanner_get_cells_as_arrays(scanner)
            client.scanner_close(scanner)
            entries = []
            nodeIds = {}
            row     = None
            entry   = None
            for cells in results:
                if row != cells[0]:
                    if entry:
                        entries.append(entry)
                    entry = LightEntry()
                    entry.path.row = cells[0]
                    row = cells[0]
                key = cells[1]
                if cells[2]:
                    key = "%s:%s" % (cells[1],cells[2])
                entry.path[key] = cells[3]
                if key == 'id':
                    # make the linking to the ids
                    nodeIds[entry.path[key]] = entry.node
            if entry:
                entries.append(entry)
                    
            logging.getLogger().debug('Scan hypertable: %s' % (time.time() - start))

            if len(nodeIds):
                start = time.time()
		
		# warning: Due to bug in Hypertable max 118 items are fetched, therefore we need to separate the HQL query into batch of max 100 rows
		allKeys = nodeIds.keys()
		limit = 100
		steps = (len(allKeys) / limit) + 1
		results = []
		for i in range(0,steps):
			start = i*limit
			stop  = (i+1)*limit
			keysToUse = allKeys[start:stop]
				
		        query = "SELECT * FROM nodes WHERE (";
		        for id in keysToUse:
		            query += " ROW = '%s' OR " % id
		        query = query[:-3]
		        query += ") REVS 1"

		        s = client.hql_exec(namespace,query, 0, 1)
		        scanner = s.scanner
		        result = client.scanner_get_cells_as_arrays(scanner)
		        client.scanner_close(scanner)
			results.extend(result)

                id = None
		for cells in results:
                    if id != cells[0]:
                        id = cells[0]
                        nodeIds[id].row = id
                    key = cells[1]
                    if cells[2]:
                        key = "%s:%s" % (cells[1],cells[2])
                    nodeIds[id][key] = cells[3]
                logging.getLogger().debug('Finding entries: %s' % (time.time() - start))

        return entries

    def new(self):
        return Entry()

    def delete(self, table, rows):
        allowedTables = ['paths', 'nodes']

        if not table in allowedTables:
            raise ValueError('Invalid table argument')

        (client, namespace) = self._getClientNamespace()
        query = "DELETE * FROM %s WHERE ROW='%s' ";
        for key in rows.keys():
            client.hql_exec(namespace,
                                  query % (table, key),
                                  0, 1)

    def promote(self, lightEntry):
        if not isinstance(lightEntry, LightEntry):
            return False

        path = Paths()
        path.row = lightEntry.path.row
        for key, value in lightEntry.path.items():
            path[key] = value

        node = Nodes()
        node.row = lightEntry.node.row
        for key, value in lightEntry.node.items():
            node[key] = value

        lightEntry.path = path
        lightEntry.node = node

        return True

    def _getClientNamespace(self):
        if not self.connectionWrapper:
            self.connectionWrapper = ConnectionPool().get()
        return self.connectionWrapper.getConnection()
