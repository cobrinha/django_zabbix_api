# -*- coding: utf-8 -*-
# importa bibliotecas piston
from piston.resource import Resource
from piston.handler import BaseHandler
from piston.utils import rc

# importa bibliotecas django
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

# importa os models
from api.models import *

# importa lib local
from lib.log import Log
from lib.error import raiseError

# importa outras lib
import local,json,re,datetime,copy

#importa zabbix
from api.zabbix import Zabbix

import string
import random

class ZabbixMassAdd:
    def __init__(self, user_group_id, host_group_id):
        #definindo parametros de usuario e grupo
        self.user_group_id        = user_group_id       
        self.host_group_id        = host_group_id       

    def Add(self, request):
        api_obs = u"Inclusao de permissao para grupo de usuarios em grupos de hosts no Zabbix"
        api_log_referencia_id = None
        api_log_action_nome = "criar"
        api_log_tipo_nome = "zab"
        alog = Log.saveAlog(request)

        #buscando id do servidor
        try:
            servidor   = Servidor.objects.get(nome=local.SERVER_ZABBIX_DEFAULT)
        except  ObjectDoesNotExist:
            return raiseError(alog,"server_not_exist",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome) 
        else:
            self.usuario_servidor = servidor.id

        # valores caso nao consiga incluir usuario no Zabbix
        error_transaction = None
        grupo_usuario_tentativa = 1
        status   = Status.objects.get(label='INCLUIR')
        usrgrpids = 0

        # tentando incluir grupo de usuarios em grupos de host no Zabbix
        try:
            zab_usuario    = local.SERVER_ZABBIX[servidor.nome]['usuario']
            zab_senha       = local.SERVER_ZABBIX[servidor.nome]['senha']
            zab = Zabbix()
            zab.setHost(servidor.endereco)
            zab.setUser(zab_usuario)
            zab.setPassword(zab_senha)
            if zab.login() == True:
                create_resp = zab.massAddUserGroup( self.user_group_id, self.host_group_id)
                if create_resp :
                    jresp = json.loads(create_resp)
                    usrgrpids = int(jresp['result']['usrgrpids'][0])
        except Exception, error:
                return False

        #retornando da inclusao
        if error_transaction:
            return raiseError(alog,"error_in_transaction",request,error_transaction,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            retorno = {
                "Success":True,
                "UserGroupIds": usrgrpids
            }
            return retorno






