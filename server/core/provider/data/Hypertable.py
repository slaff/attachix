# -*- coding: utf-8 -*-
import logging

import base
from core.pool.Hypertable import ConnectionPool
from hyperthrift.gen.ttypes import *

class ActiveRecord(base.ActiveRecord):
    
    def __init__(self):
        base.ActiveRecord.__init__(self)

    def find(self, row):
        """
        Finds an element with the specified row and preloads the data

        @param string row
        @return boolean
        """
        (client, namespace) = self._getClientNamespace()
        cells = client.get_row(namespace, self._table, "%s" % row)
        if not len(cells):
            return False

        self.setRow(cells[0].key.row)
        for cell in cells:
            key = "%s:%s" % (cell.key.column_family , cell.key.column_qualifier)
            self._data[key] = cell.value

        return True

    def findRange(self, startRow, stopRow, columns=[]):
        """
        Finds list of elements that start with startRow and ends with the endRow key.
        Notice: Implement this method in the child class.

        @param string startRow
        @param string endRow
        @param list columns
        @return list
        """
        (client, namespace) = self._getClientNamespace()
        scanner = client.scanner_open(namespace, self._table,
                   ScanSpec(
                            row_intervals=[RowInterval(
                                start_row=startRow,
                                end_row=stopRow
                            )],
                            return_deletes=False,
                            # revs=1,
                            columns=columns
                            )
                  )

        results = client.scanner_get_cells_as_arrays(scanner)
        client.scanner_close(scanner)

        elements = []
        lastKey = ""
        element = None
        for result in results:
            if result[0]!=lastKey:
                element = ActiveRecord()
                element._table = self._table
                element.setRow(result[0])
                elements.append(element)
                lastKey = result[0]
            
            element["%s:%s" % (result[1], result[2])] = result[3]

        return elements

    
    def findByColumns(self, columnFamily=[]):
        (client, namespace) = self._getClientNamespace()
        scanner = client.scanner_open(namespace, self._table,
                   ScanSpec(
                            return_deletes=False,
                            # revs=1,
                            columns=columnFamily
                            )
                   )
        results = client.scanner_get_cells_as_arrays(scanner)
        client.scanner_close(scanner)

        logging.getLogger().debug("findByColumns(%s): %s" % (columnFamily, results))

        elements = []
        lastKey = ""
        element = None

        for result in results:
            if result[0]!=lastKey:
                element = ActiveRecord()
                element._table = self._table
                element.setRow(result[0])
                elements.append(element)
                lastKey = result[0]

            element["%s:%s" % (result[1], result[2])] = result[3]

        return elements

    
    def save(self):
        """
        Save the data for the specified row
        """
        base.ActiveRecord.save(self)
        mutations = []
        for key, change in self._changedFields.items():
            column = key
            family = ''

            bits = column.split(':',1)
            if len(bits) == 2:
                column = bits[0]
                family = bits[1]
            
            if change < 0:
                flag = KeyFlag.DELETE_CF
                if family !='':
                    flag = KeyFlag.DELETE_CELL
                mutation = [self.row, column, family, '',
                           '-9223372036854775806','-9223372036854775806',
                           '%d' % flag]
            else:
                value = self._data[key]
                mutation = [self.row, column, family, value]
            mutations.append(mutation)

        if len(mutations):
            logging.getLogger().debug("Table: %s, Mutations: %s" % (self._table, mutations))
            (client, namespace) = self._getClientNamespace()
            mutator = client.mutator_open(namespace, self._table, 0, 0)
            client.mutator_set_cells_as_arrays(mutator, mutations)
            client.mutator_flush(mutator)
            client.mutator_close(mutator)


    def inc(self, key, value):
        """
        Increments a key.

        In Hypertable the cell must be defined with option COUNTER.

        @param string key - key to increment
        @param int value - number to use
        """
        bits = key.split(':',1)
        qualifier = ''
        if len(bits) > 1:
            key    = bits[0]
            qualifier = bits[1]
        value = int(value)
        if value < 0:
            value = "-%d" % abs(value)
        else:
            value = "+%d" % abs(value)

        (client, namespace) = self._getClientNamespace()
        mutator = client.mutator_open(namespace, self._table, 0, 0)
        client.mutator_set_cell(mutator, Cell(Key(row=self.row,
                                               column_family=key,
                                               column_qualifier=qualifier
                                              ), value))
        client.mutator_flush(mutator)
        client.mutator_close(mutator)

    def delete(self):
        """
        Deletes a row
        """
        (client, namespace) = self._getClientNamespace()
        mutator = client.mutator_open(namespace, self._table, 0, 0)
        client.mutator_set_cell(mutator, Cell(Key(row=self.row, flag=KeyFlag.DELETE_ROW), ""))
        client.mutator_flush(mutator)
        client.mutator_close(mutator)

    def _getClientNamespace(self):
        return ConnectionPool().get().getConnection()
