# -*- coding: utf-8 -*-

"""
Webdav XML Property Formatter
"""
import logging
import re
import time
from urllib import quote as urlquote
import xml.etree.cElementTree as ET

from copy import copy
def createMutlipartResponse(requestPath, meta, requestedProperties,postfix):
    rootEl = ET.Element("{DAV:}multistatus")
    for (path, data) in meta.items():
        responseEl = ET.SubElement(rootEl, '{DAV:}response')
        hrefEl = ET.SubElement(responseEl, '{DAV:}href')
        href = path.replace(requestPath, postfix,1)
        href = re.sub(r'/{2,}', '/', href)
        hrefEl.text = urlquote(href, safe='/')
        propstatEl = ET.SubElement(responseEl, '{DAV:}propstat')
        propEl = ET.SubElement(propstatEl, '{DAV:}prop')
        missingProperties = copy(requestedProperties)
        for (key, value) in data.items():
            if len(requestedProperties) > 0 and not requestedProperties.has_key(key):
                continue
            if key[0:1] != '{':
                # The following brakes some webdav clients
                # There it is allowed only for the litmus tests
                #if not ( request.env.has_key('HTTP_User-Agent') and \
                #request.env['HTTP_User-Agent'][0].find('litmus') > -1):
                    # if no namespace is given then assign 'none:' as default namespace
                    key = "{none:}%s" % key
            addXmlProp(propEl, key, value)
            if len(missingProperties) and missingProperties.has_key(key):
                del missingProperties[key]
        statEl = ET.SubElement(propstatEl, '{DAV:}status')
        statEl.text = "HTTP/1.1 200 OK"
        if len(missingProperties):
            missingPropstatEl = ET.SubElement(responseEl, '{DAV:}propstat')
            missingPropEl = ET.SubElement(missingPropstatEl, '{DAV:}prop')
            for property in missingProperties:
                ET.SubElement(missingPropEl, property)
            missingStatEl = ET.SubElement(missingPropstatEl, '{DAV:}status')
            missingStatEl.text = "HTTP/1.1 404 Not Found"
    return rootEl

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