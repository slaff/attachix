"""
Class with helpful design patterns
"""

class Registry():
    """
    Registry design pattern
    """
    storage = {}

    @classmethod
    def get(cls, key):
        """
        Gets key data from the registry.
        Return the element data or raises KeyValue exception
        """
        return cls.storage[key]

    @classmethod
    def set(cls, key, data):
        """
        Sets element to the registry.
        """
        cls.storage[key] = data

    @classmethod
    def exists(cls, key):
        """
        Checks if a key is already associated with data in the registry
        """
        if cls.storage.get(key):
            return True
        else:
            return False

    @classmethod
    def delete(cls, key):
        """
        Deletes key from the registry
        """
        if not cls.exists(key):
            return False
        else:
            del cls.storage[key]
            return True

    def __repr__(self):
        print cls.storage


import time
import logging
class TableDataGateway():
    """
    Class that abstracts the basic operations with a database
    """

    db = None
    table = None
    def __init__(self, db, table):
        self.db = db
        self.table = table

    def sequence(self):
        """
        Gets the next sequence id for a table
        """
        return None

    def select(self, fields, where):
        quotedFields = []
        if not len(fields):
            quotedFields.append('*')
        else:
            for field in fields:
                quotedFields.append(self.quoteIdentifier(field))
        query = 'SELECT '+ ','.join(quotedFields) + ' '+\
                'FROM '  + self.quoteIdentifier(self.table) + ' '+\
                'WHERE ' + where
        cursor = self.query(query)
        rows = cursor.fetchall()

        if not len(fields):
            fields = [i[0] for i in cursor.description]

        return [fields,rows]

    def insert(self, fields):
        """
        Insert fields into the table
        """
        selectedFields = []
        selectedValues = []
        for (name, value) in fields.items():
            selectedFields.append(self.quoteIdentifier(name))
            selectedValues.append(self.quote(value))

        query = 'INSERT INTO '+ self.quoteIdentifier(self.table) + \
                '('+','.join(selectedFields)+') VALUES ('+ \
                ','.join(selectedValues)+')'
        self.query(query)
        return self.lastId

    def update(self, fields, where):
        """
        Updates fields into the table
        """
        query = 'UPDATE '+ self.quoteIdentifier(self.table) + ' SET '
        for (name, value) in fields.items():
            query += self.quoteIdentifier(name)+'='+self.quote(value)+','
        query = query[:-1]+' WHERE '+where
        return self.query(query)

    def delete(self,fields):
        """
        Deletes records from the table using the fields
        """
        query = 'DELETE FROM '+ self.quoteIdentifier(self.table) + ' WHERE '
        for (name, value) in fields.items():
            query += self.quoteIdentifier(name)+'='+self.quote(value)+' AND '
        query = query[:-4]
        return self.query(query)
    
    def quote(self,value):
        """
        Quotes value to prevent SQL query injections
        """

        if value is None:
            return 'null'
        return "'%s'" % (value)

    def quoteIdentifier(self, value):
        """
        Quotes database identifiers to prevent SQL query injections
        """
        return "`%s`" % (value)
    

    def query(self, query):
        """
        Quotes value to prevent SQL query injections
        """

        start = time.time()
        cursor = self.db.cursor()
        logging.getLogger().debug("Q:[%s]" % (query) )
        cursor.execute(query)
        end = time.time()
        logging.getLogger().debug("T:[%.6f]" % (end-start) )
        warnings = cursor.fetchwarnings()
        if warnings:
            logging.getLogger().debug(warnings)

        self.lastId = cursor.getlastrowid()
        return cursor

class ActiveRecord(object):
    """
    Table to DB Object mapping
    The _definition must be set in the extending class.
    The following self._definition['id'] = '<table-column-id>'
    if the primary key name is different than 'id'
    """
    _definition = {
        # 'name': 'table-column-name',
        # 'id': 'table-column-id'
    }

    _dependent = {}
    """
    In order to define that a table is dependent on this one one can use
    definition like the one below
    _dependent = {
        'meta': {
            'class': Meta,
            'refKey': 'meta'
        }
    }
    """

    _alias  = {}
    """
    For making cool things like

    self.location = self.getDependent('meta').location

    _alias = {
        # field : dependent table
        'location': 'meta'
    }
    """

    _table = None
    _data = {}
    _reverseDefinition = {}
    _likeData = {} # used only for the deletion
    _changedFields = {}
    _dependentObjects = {}
    new         = None
    db          = None
    dbTableDataGateway = None

    DB_HANDLER  = TableDataGateway

    def __init__(self, db=None, id=None):
        object.__setattr__(self, 'new',True)
        object.__setattr__(self, '_data',{})
        object.__setattr__(self,'_likeData',{})
        object.__setattr__(self,'_changedFields',{})
        object.__setattr__(self,'_dependentObjects',{})
        object.__setattr__(self,'db',db)
        
        if not self._definition.has_key('id'):
            # adding default id definition
            self._definition['id'] = 'id'
        self.id = id
        if self._table is None:
            object.__setattr__(self,'_table',self.__class__.__name__.lower())

        if db is None:
            # try to get the db from the registry
            db = Registry.get('core.db')

        object.__setattr__(self,'dbTableDataGateway',ActiveRecord.DB_HANDLER(db,self._table))

        object.__setattr__(self,'_reverseDefinition',{})
        for name, column in self._definition.items():
            if name != column:
                self._reverseDefinition[column] = name
        if self.id:
            self.load(True)

    def load(self, force=False):
        if len(self._data) and not force:
            return True

        if not len(self._definition):
            raise ValueError('The definition is not set correctly')

        where = "%s='%s'" % (self._definition['id'],self.id)
        [fields, rows] = self.dbTableDataGateway.select(self._definition.values(), where)
        numRows = len(rows)
        if numRows == 1:
            self.preLoad(fields, rows[0])
        elif numRows > 1:
            raise ValueError('Too many records found')
        elif numRows < 1:
            raise KeyError('No records found')


    def preLoad(self, fields, data):
        """
        Preloads the object with existing data
        """
        for index, value in enumerate(data):
            """
            If a table column name is different than the attribute name
            then we need to re-map these fields
            """
            key = self._reverseDefinition.get(fields[index],fields[index])
            self.__setattr__(key,value)
        object.__setattr__(self, 'new', False)
        object.__setattr__(self, '_changedFields', {})

    def getPrimaryKey(self):
        try:
            primaryKey = self._data['id']
        except KeyError:
            primaryKey = None
            
        return primaryKey

    def setNew(self, flag):
        """
        @param boolean flag
        """
        if flag == True and self.new != flag:
            if len(self._data):
                # mark all data as changed
                for (name, _) in self._data.items():
                    self._changedFields[name] = 1

        elif flag == False and self.new != flag:
            object.__setattr__(self, '_changedFields', {})

        object.__setattr__(self, 'new', flag)

    def setDb(self, db):
        # @todo: Check if the change of the DB changes it also in the
        # instantiated table data gateway object
        object.__setattr__(self, 'db', db)

    def __setattr__(self, name, value):
        if self._definition.has_key(name):
            self._data[name] = value
            self._changedFields[name] = 1
            return True
        elif self._alias.has_key(name):
            setattr(self.getDependent(self._alias[name]),name,value)
            return True

        raise ValueError("This field '%s' is not allowed" % name)

    def __getattr__(self, name):
        if self._definition.has_key(name):
            return self._data.get(name,None)
        elif self._alias.has_key(name):
            return getattr(self.getDependent(self._alias[name]),name)
        
        raise KeyError('the field "%s" is not valid' % name)

    def getDependent(self, name):
        """
        Gets dependent objects
        """
        if not self._dependentObjects.has_key(name):
            dependentObject = self._dependent[name]['class'](self.db)
            try:
                refKey = getattr(self, self._dependent[name]['refKey'])
            except:
                refKey = None

            if refKey:
                dependentObject.id = refKey
                dependentObject.load(True)

            self._dependentObjects[name] = dependentObject
            
        return self._dependentObjects[name]

    def setLike(self, name, value):
        self._likeData[name] = value

    def save(self, force=False):
        if force or len(self._changedFields):
            tableData = {}
            for name in self._changedFields:
                if name == 'id':
                    continue
                tableData[self._definition[name]] = self._data[name]

            primaryKey = self.getPrimaryKey()
            if self.new:
                # check if the fields of some of the dependent objects is already set
                for (name,_) in self._dependent.items():
                    if getattr(self, name):
                        # initialize the dependent tables
                        self.getDependent(name)
                
                for (name, dependentObject) in self._dependentObjects.items():
                    # save changes to the dependent tables
                    dependentObject.save()
                    
                    tableData[self._dependent[name]['refKey']] = dependentObject.id
                    self.__setattr__(self._dependent[name]['refKey'],dependentObject.id)
               
                if primaryKey is None:
                    self.id = self.dbTableDataGateway.sequence()
                tableData[self._definition['id']] = self.id
                self.dbTableDataGateway.insert(tableData)
                object.__setattr__(self,'new',False)
                if self.dbTableDataGateway.lastId:
                    self.id = self.dbTableDataGateway.lastId
            else:
                self.dbTableDataGateway.update(tableData,
                                        "%s='%s'" % (self._definition['id'],primaryKey)
                                        )
            object.__setattr__(self,'_changedFields',{})

    def delete(self):
        """
        Removes record from the permanent storage
        Use all of the fields that are given
        plus the like data

        @return int number of affected rows
        """

        fields = {}
        if self._data.get('id',None):
            fields[self._definition['id']] = self._data['id']
        else:
            for name, value in self._data,item():
                fields[self._definition['name']] = value

        # delete the dependent objects first
        for (name, _) in self._dependent.items():
            dependentObject = self.getDependent(name)
            if not dependentObject.new:
                dependentObject.delete()

        # and after that the main object
        self.dbTableDataGateway.delete(fields)

    def __repr__(self):
        text = "Table: %s, New: %s\n" % (self._table, self.new)
        for key in self._definition:
            if self._data.has_key(key):
                changed = ''
                if self._changedFields.has_key(key):
                    changed = '*'
                text+= "\t%s=%s %s\n" % (key, self._data[key],changed)
        return text

class Decorator(object):
    """
    Decorator Pattern to adding additional features (methods, attributes) to existing objects
    """
    __slots__ = ['_obj','__weakref__']
    
    def __init__(self, obj):
        object.__setattr__(self, "_obj", obj)

    def __getattr__(self, name):
        return getattr(object.__getattribute__(self, "_obj"), name)

    def __delattr__(self, name):
        delattr(object.__getattribute__(self, "_obj"), name)

    def __setattr__(self, name, value):
        if hasattr(self, name):
            self.name = value
            return

        setattr(object.__getattribute__(self, "_obj"), name, value)

    def __nonzero__(self):
        return bool(object.__getattribute__(self, "_obj"))

    def __str__(self):
        return str(object.__getattribute__(self, "_obj"))
    def __repr__(self):
        return repr(object.__getattribute__(self, "_obj"))

    def __del__(self):
        # remove references to the object - if this is not done
        # they most certainly will not be cleaned
        object.__delattr__(self, '_obj')