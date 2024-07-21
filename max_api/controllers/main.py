# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# import logging
# from contextlib import contextmanager

# from werkzeug.exceptions import BadRequest

from odoo.http import Controller, ControllerType, Response, request, \
    controllers_per_module

from odoo import _, fields, http, tools, SUPERUSER_ID
import json
import werkzeug

class HttpController(http.Controller):
    

    @http.route('/api/v1/health', type='http', auth='none', methods=['GET'], csrf=False)
    def health(self, **kwargs):
        return Response("OK", status=200)

    @http.route('/api/v1/search', type='http', auth='none', methods=['GET'], csrf=False)
    def search(self, **kwargs):
        json_data = {}
        try:
            json_data = json.loads(request.httprequest.data)
        except:
            return Response("Invalid JSON data", status=400)
        
        model = kwargs.get('model') or json_data.get('model')
        domain = kwargs.get('domain') or json_data.get('domain')
        fields = kwargs.get('fields') or json_data.get('fields')
        limit = kwargs.get('limit') or json_data.get('limit')

        if not model:
            return Response("Model is required", status=400)

        if not domain:
            domain = []
        if isinstance(domain, str):
            try:
                domain = json.loads(domain)
            except:
                return werkzeug.wrappers.Response("Fields must be a list of string", status=400)

        if not fields:
            fields = ['id', 'name']
        if isinstance(fields, str):
            try:
                fields = json.loads(fields)
            except:
                return werkzeug.wrappers.Response("Fields must be a list of string", status=400)

        if not limit:
            limit = 1

        try:
            model = request.env[model].sudo()
            records = model.search(domain, limit=limit)
            return werkzeug.wrappers.Response(str(records.read(fields)), status=200, content_type='application/json')
        except Exception as e:
            return werkzeug.wrappers.Response(str(e), status=500)



# from odoo.addons.component.core import WorkContext, _get_addon_name

# from ..core import _rest_controllers_per_module

# _logger = logging.getLogger(__name__)


# class _PseudoCollection(object):
#     __slots__ = "_name", "env"

#     def __init__(self, name, env):
#         self._name = name
#         self.env = env


# class RestControllerType(ControllerType):

#     # pylint: disable=E0213
#     def __init__(cls, name, bases, attrs):  # noqa: B902
#         if (
#             "RestController" in globals()
#             and RestController in bases
#             and Controller not in bases
#         ):
#             # to be registered as a controller into the ControllerType,
#             # our RestConrtroller must be a direct child of Controller
#             bases += (Controller,)
#         super(RestControllerType, cls).__init__(name, bases, attrs)
#         # The generic controller should not be registered as a controller
#         # even if it inherits from Controller
#         base_rest_controllers = controllers_per_module['base_rest']
#         name_class = ("%s.%s" % (cls.__module__, 'RestController'), cls)
#         if name_class in base_rest_controllers:
#             base_rest_controllers.remove(name_class)

#         if "RestController" not in globals() or not any(
#             issubclass(b, RestController) for b in bases
#         ):
#             return
#         # register the rest controller into the rest controllers registry
#         root_path = getattr(cls, "_root_path", None)
#         collection_name = getattr(cls, "_collection_name", None)
#         if root_path and collection_name:
#             if not hasattr(cls, "_module"):
#                 cls._module = _get_addon_name(cls.__module__)
#             _rest_controllers_per_module[cls._module].append(
#                 {
#                     "root_path": root_path,
#                     "collection_name": collection_name,
#                     "controller_class": cls,
#                 }
#             )


# class RestController(Controller, metaclass=RestControllerType):
#     """Generic REST Controller

#     This controller provides generic routes conform to commen REST usages.
#     You must inherit of this controller into your code to register your REST
#     routes. At the same time you must fill 2 required informations:

#     _root_path:
#     _collection_name:

#     """

#     _root_path = None
#     _collection_name = None
#     # The default authentication to apply to all pre defined routes.
#     _default_auth = "user"
#     # You can use this parameter to specify an authentication method by HTTP
#     # method ie: {'GET': None, 'POST': 'user'}
#     _auth_by_method = {}
#     # The default The Access-Control-Allow-Origin cors directive value.
#     _cors = None
#     # Whether CSRF protection should be enabled for the route.
#     _csrf = False

#     def _get_component_context(self):
#         """
#         This method can be inherited to add parameter into the component
#         context
#         :return: dict of key value.
#         """
#         return {"request": request}

#     def make_response(self, data):
#         if isinstance(data, Response):
#             # The response has been build by the called method...
#             return data
#         # By default return result as json
#         return request.make_json_response(data)

#     @property
#     def collection_name(self):
#         return self._collection_name

#     @property
#     def collection(self):
#         return _PseudoCollection(self.collection_name, request.env)

#     @contextmanager
#     def work_on_component(self):
#         """
#         Return the component that implements the methods of the requested
#         service.
#         :param service_name:
#         :return: an instance of base.rest.service component
#         """
#         collection = self.collection
#         params = self._get_component_context()
#         yield WorkContext(
#             model_name="rest.service.registration", collection=collection, **params
#         )

#     @contextmanager
#     def service_component(self, service_name):
#         """
#         Return the component that implements the methods of the requested
#         service.
#         :param service_name:
#         :return: an instance of base.rest.service component
#         """
#         with self.work_on_component() as work:
#             service = work.component(usage=service_name)
#             yield service

#     def _validate_method_name(self, method_name):
#         if method_name.startswith("_"):
#             _logger.error(
#                 "REST API called with an unallowed method "
#                 "name: %s.\n Method can't start with '_'",
#                 method_name,
#             )
#             raise BadRequest()
#         return True

#     def _process_method(self, service_name, method_name, *args, params=None):
#         self._validate_method_name(method_name)
#         with self.service_component(service_name) as service:
#             result = service.dispatch(method_name, *args, params=params)
#             return self.make_response(result)
