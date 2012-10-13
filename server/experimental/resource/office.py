# -*- coding: utf-8 -*-
import logging
import vobject
import xml.etree.cElementTree as ET

from core.properties import createMutlipartResponse
import core.provider.storage as storage
from core.resource.base import WebdavResource
from core.utils import getMD5

class CaldavResource(WebdavResource):
    """
    Resource for keeping calendar events.
    CalDAV resource implementation based on RFC 4791
    http://tools.ietf.org/html/rfc4791
    """
    def __init__(self, *args, **kwargs):
        """
        @param calendarProvider 
        """
        self.calendarProvider = kwargs.pop('calendarProvider')
        WebdavResource.__init__(self, *args, **kwargs)

    def render_GET(self, request):
        result = WebdavResource.render_GET(self, request)
        user = request.env.get('user')
        if not self.storageProvider.isCollection(request.path, user=user) and \
        self.calendarProvider.isCalendar(request.path, user=user):
            request.setHeader('Content-Type','text/calendar; charset=utf-8')
        return result

    def render_OPTIONS(self, request):
        WebdavResource.render_OPTIONS(self, request)
        request.setHeader('DAV', '1, 2, access-control, calendar-access')

    def render_MKCALENDAR(self, request):
        if self._isLocked(request):
            request.setResponseCode(423)
            return

        user = request.env.get('user')
        # if the path exists then bail out with error
        if self.storageProvider.exists(request.path, user=user):
            # (DAV:resource-must-be-null): A resource MUST NOT exist at the Request-URI;
            responseBody = """<?xml version="1.0">
<error xmlns="DAV:">
    <resource-must-be-null/>
</error>"""
            request.write(responseBody)
            request.setResponseCode(403)
            return

        root = None
        if request.env.has_key('CONTENT_LENGTH') and \
        long(request.env['CONTENT_LENGTH'].strip()) > 0:
            try:
                tree = ET.parse(request);
                root = tree.getroot()
            except:
                request.setResponseCode(400)
                return

        try:
            self.storageProvider.createCollection(request.path, user=user)
        except EnvironmentError as e:
            logging.getLogger().warn("@todo: Handle delete exceptions from the storage provider %s" % e)
            if e.errno == storage.PRECONDITION_FAILED:
                request.setResponseCode(409)
            else:
                request.setResponseCode(405)
            return

        if root is not None:
            allProps = {} # hash with property name and its status
            sets = root.findall('./{DAV:}set')
            if sets:
                for set in sets:
                    props = set.findall('./{DAV:}prop')
                    for prop in props:
                        for tag in prop:
                            allProps[tag.tag] = 0
                            try:
                                self.storageProvider.setMeta(request.path, {tag.tag: tag.text}, user=user)
                            except Exception, ex:
                                logging.getLogger().error("setMeta: Got Exception: %s" % ex)
                                allProps[tag.tag] = 1
        

        request.setResponseCode(201)
        return {request.path: {}}

    def render_PUT(self, request):
        result = WebdavResource.render_PUT(self, request)
        if result is not None and result.has_key(request.path) and \
        request.env['CONTENT_TYPE'].strip().find('text/calendar') == 0:
            user=request.env.get('user')
            stream = self.storageProvider.get(request.path, user=user)
            try:
                event = vobject.readOne(stream)
                self.calendarProvider.store(request.path, event, user=user)

                # generate the etag data and add it to the document.
                stream.seek(0)
                md5Sum = getMD5(stream)
                md5Sum.update(request.path)
                etag = md5Sum.hexdigest()

                self.storageProvider.setMeta(request.path,
                                        {'{DAV:}getetag': "%s" % etag,
                                         '{DAV:}getcontenttype': 'text/calendar'
                                        },
                                        user=user
                                 )
            except Exception as ex:
                logging.getLogger().warn('Not a calendar object. Got error: %s' % ex)
            finally:
                stream.close()
        return result

    def render_REPORT(self, request):
        try:
            tree = ET.parse(request);
            root = tree.getroot()
        except:
            request.setResponseCode(400)
            return

        """
<C:calendar-query xmlns:C="urn:ietf:params:xml:ns:caldav" xmlns:D="DAV:">
  <D:prop>
    <D:getetag/>
  </D:prop>
  <C:filter>
    <C:comp-filter name="VCALENDAR">
      <C:comp-filter name="VEVENT">
        <C:time-range start="20120907T104015Z" end="20121116T104015Z"/>
      </C:comp-filter>
    </C:comp-filter>
  </C:filter>
</C:calendar-query>
        """

        """
<C:calendar-multiget xmlns:C="urn:ietf:params:xml:ns:caldav" xmlns:D="DAV:">
  <D:prop>
    <D:getetag/>
    <C:calendar-data/>
  </D:prop>
  <D:href>/calendar</D:href>
</C:calendar-multiget>
        """
        requestedProperties = {} # hash with property name and its status
        props = root.findall('./{DAV:}prop')
        for prop in props:
            for tag in prop:
                requestedProperties[tag.tag] = 0

        hrefs = root.findall('./{DAV:}href')
        requestedHrefs = []
        for href in hrefs:
            for tag in href:
                requestedHrefs.append(tag.text)

        user=request.env.get('user')
        paths = {}
        if root.tag == "{urn:ietf:params:xml:ns:caldav}calendar-multiget":
            # get all items in the requested calendar folder
            if len(requestedHrefs) == 1:
                paths[request.path] = 1
            else:
                for href in requestedHrefs:
                    path = href.replace(request.uri,request.path,1)
                    paths[path] = 0
        elif root.tag == "{urn:ietf:params:xml:ns:caldav}calendar-query":
            ranges = []
            filters = root.findall('./{urn:ietf:params:xml:ns:caldav}filter/{urn:ietf:params:xml:ns:caldav}comp-filter')
            for filter in filters:
                if filter.attrib['name'].upper()=='VCALENDAR':
                    eventFilters = filter.findall('./{urn:ietf:params:xml:ns:caldav}comp-filter')
                    for eventFilter in eventFilters:
                        if eventFilter.attrib['name'].upper()=='VEVENT':
                            timeRanges = eventFilter.findall('./{urn:ietf:params:xml:ns:caldav}time-range')
                            for timeRange in timeRanges:
                                ranges.append("%s:%s" % (timeRange.attrib['start'], timeRange.attrib['end']))
            paths = self.calendarProvider.search(request.path, {'time-range': ranges})

        events = {}
        for path,depth in paths.items():
            try:
                event   = self.storageProvider.getMeta(path, depth, requestedProperties, user=user)
            except (OSError, IOError), e:
                # Some User-Agents, like Konqueror want to have also response body
                request.writeDirect('<html><body><h1>Not Found</h1></body></html>', 404)
                logging.getLogger().error("render_PROPFIND(): got exception %s" % e)
                if path==request.path:
                    return
                else:
                    # @todo: provide the correct meta data for missing path
                    pass
            events.update(event)

        meta = {}
        for path, event in events.items():
            meta[path] = event
            if requestedProperties.has_key('{urn:ietf:params:xml:ns:caldav}calendar-data') \
            and event['{DAV:}resourcetype'] == 0:
                stream = self.storageProvider.get(path ,user=user)
                calendarData = stream.read()
                stream.close()
                meta[path]['{urn:ietf:params:xml:ns:caldav}calendar-data'] = calendarData
     
        request.setHeader('Content-Type', 'text/xml; charset="utf-8"')
        rootEl = createMutlipartResponse(request.path, meta, requestedProperties, request.uri)
        responseBody = '<?xml version="1.0" encoding="utf-8" ?>' + "\n" + \
                       '<?xml-stylesheet type="text/xsl" href="/~static/propfind.xslt"?>' + "\n" +\
                      ET.tostring(rootEl)
        request.writeDirect(responseBody, 207)

    def render_PROPFIND(self,request):
        request.env['HTTP_ACCEPT']='text/xml'
        if request.env.has_key('HTTP_X_REQUESTED_WITH'):
            del request.env['HTTP_X_REQUESTED_WITH']
        return WebdavResource.render_PROPFIND(self, request)

class CardavResource(WebdavResource):
    """
    Resource for keeping address book contacts.
    CardDAV resource implementation based on RFC 6352
    http://www.ietf.org/rfc/rfc6352.txt

    """

    def __init__(self, *args, **kwargs):
        """
        @param contactProvider 
        """
        self.contactProvider = kwargs.pop('contactProvider')
        WebdavResource.__init__(self, *args, **kwargs)

    def render_OPTIONS(self, request):
        WebdavResource.render_OPTIONS(self, request)
        request.setHeader('DAV', '1, 2, access-control, addressbook')
        request.setHeader('Allow', 'REPORT, ACL')

    def render_MKCOL(self, request):
        if self._isLocked(request):
            request.setResponseCode(423)
            return

        user = request.env.get('user')
        # if the path exists then bail out with error
        if self.storageProvider.exists(request.path, user=user):
            # (DAV:resource-must-be-null): A resource MUST NOT exist at the Request-URI;
            responseBody = """<?xml version="1.0">
<error xmlns="DAV:">
    <resource-must-be-null/>
</error>"""
            request.write(responseBody)
            request.setResponseCode(403)
            return

        try:
            tree = ET.parse(request);
            root = tree.getroot()
        except:
            request.setResponseCode(400)
            return

        allProps = {} # hash with property name and its status
        sets = root.findall('./{DAV:}set')
        if sets:
            for set in sets:
                props = set.findall('./{DAV:}prop')
                for prop in props:
                    for tag in prop:
                        allProps[tag.tag] = 0
                        try:
                            self.storageProvider.setMeta(request.path, {tag.tag: tag.text}, user=user)
                        except Exception, ex:
                            logging.getLogger().error("setMeta: Got Exception: %s" % ex)
                            allProps[tag.tag] = 1

        try:
            self.storageProvider.createCollection(request.path, user=user)
        except EnvironmentError as e:
            logging.getLogger().warn("@todo: Handle delete exceptions from the storage provider %s" % e)
            if e.errno == storage.PRECONDITION_FAILED:
                request.setResponseCode(409)
            else:
                request.setResponseCode(405)
            return

        request.setResponseCode(201)

    def render_PUT(self, request):
        result = WebdavResource.render_PUT(self, request)
        if result is not None and result.has_key(request.path):
            user = request.env.get('user')
            stream = self.storageProvider.get(request.path, user=user)
            md5Sum = getMD5(stream)
            md5Sum.update(request.path)
            etag = md5Sum.hexdigest()
            self.storageProvider.setMeta(request.path,
                                        {'{DAV:}getetag': "%s" % etag},
                                        user=user
                                 )
            stream.seek(0)
            event = vobject.readOne(stream)
            self.contactProvider.store(request.path, event)
        return result

    def render_REPORT(self, request):
        try:
            tree = ET.parse(request);
            root = tree.getroot()
        except Exception as ex:
            logging.getLogger().warn('Error processing the client XML: %s' % ex)
            request.setResponseCode(400)
            return

        """
<C:addressbook-multiget xmlns:D="DAV:"
                        xmlns:C="urn:ietf:params:xml:ns:carddav">
     <D:prop>
       <D:getetag/>
       <C:address-data content-type='text/vcard' version='4.0'/>
     </D:prop>
     <D:href>/home/bernard/addressbook/vcf3.vcf</D:href>
</C:addressbook-multiget>
        """

        requestedProperties = {} # hash with property name and its status
        props = root.findall('./{DAV:}prop')
        for prop in props:
            for tag in prop:
                requestedProperties[tag.tag] = 0

        hrefs = root.findall('./{DAV:}href')
        requestedHrefs = []
        for href in hrefs:
            for tag in href:
                requestedHrefs.append(tag.text)

        user=request.env.get('user')

        if root.tag != "{urn:ietf:params:xml:ns:carddav}addressbook-multiget":
            logging.getLogger().warn("Unable to process contact request tag:%s" % root.tag)

        paths = {}
        for href in requestedHrefs:
            path = href.replace(request.uri,request.path,1)
            paths[path] = 0

        contacts = {}
        for path,depth in paths.items():
            try:
                contact   = self.storageProvider.getMeta(path, depth, requestedProperties, user=user)
            except (OSError, IOError), e:
                # Some User-Agents, like Konqueror want to have also response body
                request.writeDirect('<html><body><h1>Not Found</h1></body></html>', 404)
                logging.getLogger().error("render_PROPFIND(): got exception %s" % e)
                if path==request.path:
                    return
                else:
                    # @todo: provide the correct meta data for missing path
                    pass
            contacts.update(contact)

        meta = {}
        for path, contact in contacts.items():
            meta[path] = contact
            if requestedProperties.has_key('{urn:ietf:params:xml:ns:carddav}address-data') \
            and event['{DAV:}resourcetype'] == 0:
                stream = self.storageProvider.get(path ,user=user)
                calendarData = stream.read()
                stream.close()
                meta[path]['{urn:ietf:params:xml:ns:carddav}address-data'] = calendarData

        request.setHeader('Content-Type', 'text/xml; charset="utf-8"')
        rootEl = createMutlipartResponse(request.path, meta, requestedProperties, request.uri)
        responseBody = '<?xml version="1.0" encoding="utf-8" ?>' + "\n" + \
                       '<?xml-stylesheet type="text/xsl" href="/~static/propfind.xslt"?>' + "\n" +\
                      ET.tostring(rootEl)
        request.writeDirect(responseBody, 207)

        

        