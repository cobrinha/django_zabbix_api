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

class ZabbixAction:

    def __init__(self,  nome, user_group_id, host_group_id):
        #incluindo action para o host
        self.nome                       = nome
        self.user_group_id      = user_group_id
        self.host_group_id      = host_group_id

    def Add(self, request):
        api_obs = u"Inclusao de action no Zabbix"
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

        #buscando id do host
        try:
            host    = Host.objects.get(nome=self.nome)
        except  ObjectDoesNotExist:
            return raiseError(alog,"host_not_exist",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome) 
        else:
            host_id  = host.id

        # valores caso nao consiga incluir action no Zabbix
        error_transaction = None
        self.tentativa = 1
        status   = Status.objects.get(label='INCLUIR')
        actionids = 0

        # tentando incluir action no Zabbix
        try:
            zab_usuario    = local.SERVER_ZABBIX[servidor.nome]['usuario']
            zab_senha       = local.SERVER_ZABBIX[servidor.nome]['senha']
            zab = Zabbix()
            zab.setHost(servidor.endereco)
            zab.setUser(zab_usuario)
            zab.setPassword(zab_senha)
            if zab.login() == True:
                create_resp = zab.createPingAction( self.nome, int(self.user_group_id), int(self.host_group_id))
                if  create_resp:
                    jresp = json.loads(create_resp)
                    actionids = int(jresp['result']['actionids'][0])
                    status   = Status.objects.get(label='ATIVO')
                    self.tentativa = 0
        except Exception, error:
            return False

        #incluindo action no mysql
        with transaction.commit_manually():
            try:
                action = Action(nome=self.nome,
                    label=self.nome,
                    tentativa=self.tentativa,
                    status=status,
                    host=host,
                    zabbix_id=actionids, 
                    data_criacao=datetime.datetime.now())
                action.save()
            except Exception,error:
                error_transaction = error
                transaction.rollback()
            else:
                transaction.commit()

        if error_transaction:
            return raiseError(alog,"error_in_transaction",request,error_transaction,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            #retornando da inclusao
            retorno = {
                "Success":True,
                "Actionids": actionids
            }
            return retorno

