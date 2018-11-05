# -*- coding: utf-8 -*-
# importa django e piston
from django.conf.urls.defaults  import patterns,include,url
from piston.resource            import Resource
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# importa os models
from api.handlers import servidor
from api.handlers import status
from api.handlers import usuario
#from api.handlers import host
#from api.handlers import host_teste
from api.handlers import zabbix

# importa lib local
from lib.auth import ApiKeyAuthentication

# chave de autenticacao
key_auth = ApiKeyAuthentication()

# API protect resource
class APIProtectedResource(Resource):
    def __init__(self,handler,authentication=key_auth):
        super(APIProtectedResource, self).__init__(handler,authentication)
        self.csrf_exempt = getattr(self.handler,"csrf_exempt",True)

emitter_format = {
    "emitter_format":"json"
}
urlpatterns = patterns("azabbix.api.handlers",
    url(r"^servidor/list/?$", APIProtectedResource(servidor.List), emitter_format),
    url(r"^servidor/add/?$", APIProtectedResource(servidor.Add), emitter_format),
    url(r"^servidor/update/?$", APIProtectedResource(servidor.Update), emitter_format),
    url(r"^servidor/delete/?$", APIProtectedResource(servidor.Delete), emitter_format),

    url(r"^status/list/?$", APIProtectedResource(status.List), emitter_format),
    url(r"^status/add/?$", APIProtectedResource(status.Add), emitter_format),
    url(r"^status/update/?$", APIProtectedResource(status.Update), emitter_format),

    url(r"^usuario/list/?$",APIProtectedResource(usuario.List),emitter_format),
    url(r"^usuario/add/?$", APIProtectedResource(usuario.Add), emitter_format),
    url(r"^usuario/update/?$", APIProtectedResource(usuario.Update), emitter_format),
    url(r"^usuario/delete/?$", APIProtectedResource(usuario.Delete), emitter_format),

#    url(r"^host/list/?$", APIProtectedResource(host.List), emitter_format),
#    url(r"^host/add/?$", APIProtectedResource(host.Add), emitter_format),
#    url(r"^host/update/?$", APIProtectedResource(host.Update), emitter_format),

    #url(r"^host_teste/add/?$", APIProtectedResource(host_teste.Add), emitter_format),
    #url(r"^host_teste/delete/?$", APIProtectedResource(host_teste.Delete), emitter_format),

    url(r"^zabbix/add/?$", APIProtectedResource(zabbix.Add), emitter_format),
    #url(r"^zabbix/deamon/?$", APIProtectedResource(zabbix.Deamon), emitter_format),
    url(r"^zabbix/delete/?$", APIProtectedResource(zabbix.Delete), emitter_format),

)

urlpatterns += staticfiles_urlpatterns()
