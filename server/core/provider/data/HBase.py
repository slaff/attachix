# -*- coding: utf-8 -*-
import logging

import base
from hbase.ttypes import Mutation

from core.pool.HBase import ConnectionPool

class ActiveRecord(base.ActiveRecord):
    client = None

    def __init__(self, client=None):
        if not client:
            # get the default client
            client = ConnectionPool().getConnection()
        self.client = client
        base.ActiveRecord.__init__(self)

    def find(self, row):
        """
        Finds an element with the specified row and preloads the data

        @param string row
        @return boolean
        """
        results = self.client.getRow(self._table, row)
        if not results:
            return False

        result = results[0]
        self.setRow(result.row)
        for key in result.columns:
            self._data[key] = result.columns[key].value

        return True

    def findRange(self, startRow, stopRow, columns=[]):
        """
        Finds list of elements that start with startWith key and and with the endWith key
        Notice: Implement this method in the child class.

        @param string startWith
        @param string endWith
        @param list columns
        @return list
        """
        scanner = self.client.scannerOpenWithStop(self._table, startRow, stopRow, columns)
        items = []
        while True:
            results  = self.client.scannerGet(scanner)
            if not results:
                break

            items.append(results[0])

        return items

    def save(self):
        """
        Save the data for the specified row
        """
        base.ActiveRecord.save(self)
        mutations = []
        for key, change in self._changedFields.items():
            if change < 0:
                mutation = Mutation(column="%s" % key, isDelete=True)
            elif change > 0:
                mutation = Mutation(column="%s" % key, value=self._data[key])

            mutations.append(mutation)

        logging.getLogger().debug("Table: %s, Row: %s, Mutations: %s" % (self._table, self.row, mutations))
        if len(mutations):
            self.client.mutateRow(self._table, self.row, mutations)

    def inc(self, key, value):
        """
        Increments a key

        @param string key - key to increment
        @param int value - number to use
        """
        self.client.atomicIncrement(self._table, self.row, key, value)

    def delete(self):
        """
        Deletes a row
        """
        self.client.deleteAllRow(self._table, self.row)
