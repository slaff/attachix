# @todo: Refactor this method to work as the HBase meta class !!!

from copy import copy
from core.pattern import ActiveRecord, TableDataGateway

import time

NODE_COLLECTION = 1
NODE_FILE       = 0

DEPTH_NODE      = 0
DEPTH_CHILDREN  = 1
DEPTH_INFINITY = -1

class Meta(ActiveRecord):
    _definition = {
        'location': 'location',
        'ref_count': 'ref_count'
    }

    def save(self):
        if self.new:
            self.ref_count = 0
        self.ref_count += 1
        ActiveRecord.save(self)

    def delete(self):
        """
        Decrease the ref count with 1.
        @return int Returns the current ref count. If it is below 1 than
                    the physical file has to be removed also
        """
        try:
            self.getPrimaryKey()
        except ValueError:
            raise ValueError('The id key must be set in order to delete Meta record')

        self.ref_count = self.ref_count - 1
        if self.ref_count < 1:
            ActiveRecord.delete(self)
        else:
            ActiveRecord.save(self)

        return self.ref_count


class Node(ActiveRecord):
    """
    Virtual File System.
    """
    _definition = {
        'name'      : 'name',
        'parent'    : 'parent',
        'reference' : 'reference',
        'collection': 'type',
        'path'      : 'path',
        'owner'     : 'owner',
        'user'      : 'user',
        'permission': 'permission',
        'group'     : 'group',

        'mime_major': 'mime_major',
        'mime_minor': 'mime_minor',
        'size'      : 'size',
        'modified'  : 'modified',
        'created'   : 'created',

        # reference keys
        'meta'      : 'meta'
    }

    _dependent = {
        'meta': {
            'class': Meta,
            'refKey': 'meta'
        }
    }

    _alias = {
        # field : dependent table
        'location': 'meta',
        'ref_count': 'meta'
    }

    def save(self):
        new = self.new
        ActiveRecord.save(self)
        # update the path
        if new:
            self.created = time.time()
            if self.parent:
                parentNode = Node(self.db)
                parentNode.id = self.parent
                parentNode.load(True)
                self.path = '%s%s/' % (parentNode.path, self.id)
            else:
                self.path = '/%s/' % self.id
            ActiveRecord.save(self)
    
    def getChildren(self, depth=1):
        finder = Search()
        nodes = finder.findByPath(self._data['path'], depth)
        return nodes

    def copy(self):
        node = Node(self.db)
        for (name, value) in self._data.items():
            if name == 'id':
                continue
            setattr(node,name,value)
        return node

    def link(self, name, parentNode):
        targetNode = self.copy()
        # change the db to be the db of the parentNode
        targetNode.setDb(parentNode.db)
        targetNode.name   = name
        targetNode.parent = parentNode.id
        targetNode.reference = self.id
        targetNode.save()

    def delete(self, recursively=False):
        if recursively:
            finder = Search(self.db)

            if not self._data.get('path',None):
                self.load(True)
                if not self._data['path']:
                    raise ValueError('Not enough data given')

            nodes = finder.findByIdPath(self._data['path'], DEPTH_INFINITY)
            count = 0
            for node in nodes:
                node.delete()
                count += 1
            return count

        return ActiveRecord.delete(self)

    def setProperty(self, Property):
        pass

    def getProperty(self):
        """
        @return Property
        """
        pass
    
    def setGroup(self):
        pass

    def getGroup(self):
        """
        @return VFS.Group instance
        """
        pass


class Property():
    def set(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    def load(self, nodeId):
        pass

    def save(self):
        pass

class Group():
    """
    Make it extend a hash and have

    __getiter__
    __len__
    __get__
    __set__
    __del__

    the key is the name and the value is 1
    """

    def __init__(self):
        """
        Creates new group or loads existing one
        """
        pass

    def load(self, id):
        """
        Loads information about existing group
        """
        pass

    def addUser(self):
        pass

    def removeUser(self):
        pass

    def getUsers(self):
        pass

    def delete(self):
        pass

    def save(self):
        """
        Saves any changes added to the group
        """
        pass

class Search():
    """
    Class for fast discovery of nodes
    """

    DB_HANDLER = TableDataGateway

    def __init__(self, db):
        self.dbConnection = Search.DB_HANDLER(db, 'node')

    # @todo: implement some caching here

    def findByPath(self, path, depth=0):
        """
        Finds nodes mathing the url path
        Example: /this/folder/file -> /12/34/45/5

        @return {Node} or list of Nodes depending on the depth or None if no node is found
        """
        
        try:
            names = path.strip('/').split('/')
            lenNames = len(names)
        except:
            return None

        if lenNames == 0:
            return None

        safeNames = []
        for part in names:
            safeNames.append(self.dbConnection.quote(part))

        fields = ['id','name','path','parent']
        columns = {}
        for (index, name) in enumerate(fields):
            columns[name]=index

        (_,rows) = self.dbConnection.select(fields,
                              " name in (%s)" % ','.join(safeNames))

        lastParent  = None;
        idParts     = []
        lookupTable = {}
        count = len(rows)
        i     = 0
        while i < count:
            row = rows[i]
            if len(names) > 0 and names[0] == row[columns['name']] \
            and row[columns['parent']] == lastParent:
                idParts.append('%s' % row[columns['id']])
                lastParent = row[columns['id']]
                names.pop(0)
                i = 0
            else:
                i+=1

            lookupTable[row[columns['path']]] = 1

        if lenNames!=len(idParts):
            return None

        idPath = '/' + '/'.join(idParts) + '/'
        if not lookupTable.has_key(idPath):
            return None

        return self.findByIdPath(idPath, depth)
    
    def findByIdPath(self, path, depth=0):
        """
        Finds the id of a node based on its idpath.
        Example: /usr/local/bin -> 121
        @param string idpath
        @paramt int depth if the depth parameter is positive then returns list of nodes
                          ordered by path ASC
        @return {Node} or list of {Node} or None if no node is found
        """

        if depth == DEPTH_INFINITY:
            where = "path LIKE %s" % self.dbConnection.quote(path+'%')
        else:
            where = "path=%s" % self.dbConnection.quote(path)
            if depth == 1:
                [fields, rows] = self.dbConnection.select(['id'], where)
                where = "parent=%d" % rows[0][0]

        where += ' ORDER BY path DESC '

        [fields, rows] = self.dbConnection.select([], where)
        if not len(rows):
            if depth == 0:
                return None
            else:
                return []

        results = []
        for row in rows:
            node = Node(self.dbConnection.db)
            node.preLoad(fields,row)
            results.append(copy(node))

        if depth == DEPTH_NODE:
            return results[0]
        return results

    def findById(self, id):
        """
        Finds the node by id
        @param  int id
        @return {Node} or None if the node cannot be foudn
        """
        node = Node(self.dbConnection.db)
        node.id = id
        try:
            node.load(True)
        except:
            return None
        
        return node