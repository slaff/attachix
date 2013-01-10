import logging
import ujson as json
import sys
import traceback
import urlparse

from core.http import getResponseType
from core.resource import Resource

"""
Resources that simulate the MvC pattern
"""
class ControllerResource(Resource):
    isLeaf = True

    def __init__(self, controller):
        self.controller = controller

    def _callAction(self, controllerAction, request):
        method = request.method.lower()
        params = {}

        if method == 'get':
            params = urlparse.parse_qs(request.query)
            params = dict(params)
        elif method == 'post':
            params = request.params

        view = {}
        view['json'] = '%s'
        if params.get('cb'):
            view['json'] = '%s(%s);' % (params['cb'], view['json'])
        view['xml']  = """<?xml version="1.0" encoding="utf-8" ?>
<response>%s</response>"""
        contentType = {}
        contentType['json'] = 'application/json'
        contentType['xml']  = 'text/xml'

        responseType = getResponseType(request)

        # result = {'code':['success'|'failure'], 'body': PythonType}
        try:
            result = controllerAction(request)
        except Exception, ex:
            traceback.print_exc(file=sys.stdout)
            logging.getLogger().error("ControllerResource:render(): Got exception %s" % ex)
            result = { 'code': 'failure', 'body': 'Unable to complete the action' }


        formattedResult = ""
        if result is None:
            # some controllers may decide to control themselves the response
            return

        if not hasattr(result,'get'):
            return result

        if not result.get('code'):
            result['code'] = 'success' # by default the code is success

        # format the response according to the reponse type
        if responseType == 'json':
            formattedResult = json.dumps(result)
        else:
            formattedResult = ""
            for key, value in result.items():
                formattedResult += "\t<%s>%s</%s>\n" % (key,value,key)

        request.setHeader('Content-Type', contentType[responseType])
        request.write(view[responseType] % (formattedResult))

    def render(self, request):
        method = request.method.lower()
        action = request.postpath[0].title()

        try:
            controllerAction = getattr(self.controller, method+'_'+action)
        except AttributeError:
            request.setHeader('Content-Type', 'text/plain')
            request.writeDirect('',405)
            return

        response = self._callAction(controllerAction, request)
        if response is not None:
            request.write(response)

import core.utils as utils
class RestResource(ControllerResource):
    isLeaf = True

    def __init__(self, controllerPath, auth=None):
        self.controllerPath = controllerPath
        self.auth = auth

    def render(self, request):
        method = request.method.lower()
        controller = request.postpath[0].title()
        action = request.postpath[1].title()

        try:
            klass = utils.require(self.controllerPath+'/'+controller.lower(), controller)
            controllerClass = klass(self.auth)
            controllerAction = getattr(controllerClass, method+'_'+action)
        except AttributeError:
            traceback.print_exc(file=sys.stdout)
            request.setHeader('Content-Type', 'text/plain')
            request.writeDirect('',405)
            return

        response = self._callAction(controllerAction, request)
        if response is not None:
            request.write(response)