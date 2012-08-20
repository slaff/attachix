"""
Webdav Property Formatter
"""
import time
import xml.etree.cElementTree as ET

def addXmlProp(propEl, key, value):
    # create prop element
    prop = ET.SubElement(propEl, key)

    if formatMap.has_key(key):
        formatMap[key](prop, value)
    elif type(value) == dict:
        formatDictValue(prop, value)
    elif type(value) == list:
        formatArrayValue(prop, key, value)
    else:
        prop.text = "%s" % value

# built-in formatters for XML PROPFIND response
def formatResourceType(prop, value):
    if value is None:
        value = 0
    elif type(value) == str:
        if value == '':
            value = 0
        else:
            value = int(value)
    
    if value != 0:
        ET.SubElement(prop, '{DAV:}collection')

def formatMtime(prop, value):
    prop.attrib['xmlns:b'] = 'urn:uuid:c2f41010-65b3-11d1-a29f-00aa00c14882/'
    prop.attrib['b:dt']    = 'dateTime.rfc1123'
    value = float(value)
    prop.text = time.strftime('%a, %d %m %Y %H:%M:%S', time.gmtime(value)) + ' GMT'

def formatSupportedLock(prop, value):
    for lock in value:
        lockEntryEl = ET.SubElement(prop,'{DAV:}lockentry')
        lockScopeEl = ET.SubElement(lockEntryEl,'{DAV:}lockscope')
        ET.SubElement(lockScopeEl,'{DAV:}%s' % lock[0])
        lockTypeEl  = ET.SubElement(lockEntryEl,'{DAV:}locktype')
        ET.SubElement(lockTypeEl,'{DAV:}%s' % lock[1])

def formatDictValue(prop, dictionary):
    for (name, data) in dictionary.items():
        addXmlProp(prop, name, data)

def formatCreationDate(prop,value):
    # @todo: Add also the timezone at the end
    # Format: 1997-12-01T17:42:21-08:00
    value = float(value)
    prop.text = time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(value))

def formatArrayValue(prop, name, array):
    logging.getLogger().warn("Parsing array properties is not implemented")
    pass

formatMap = {
    # 'key':'webdav-key',
    '{DAV:}getlastmodified': formatMtime,
    '{DAV:}resourcetype'   : formatResourceType,
    '{DAV:}supportedlock'  : formatSupportedLock,
    '{DAV:}creationdate'   : formatCreationDate
}