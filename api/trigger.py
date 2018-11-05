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

class ZabbixTrigger:

    def __init__(self,  nome, endereco, hostids=0):
        #incluindo trigger para o host
        self.nome              = nome
        self.label                = endereco
        self.endereco       = endereco
        self.hostids           = hostids

    def Add(self, request):
        api_obs = u"Inclusao de trigger no Zabbix"
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

        try:
            host    = Host.objects.get(nome=self.nome)
        except  ObjectDoesNotExist:
            return raiseError(alog,"host_not_exist",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome) 
        else:
            host_id  = host.id

        # valores caso nao consiga incluir trigger no Zabbix
        error_transaction = None
        self.tentativa = 1
        status   = Status.objects.get(label='INCLUIR')
        triggerids = 0

        # tentando incluir trigger no Zabbix
        try:
            zab_usuario    = local.SERVER_ZABBIX[servidor.nome]['usuario']
            zab_senha       = local.SERVER_ZABBIX[servidor.nome]['senha']
            zab = Zabbix()
            zab.setHost(servidor.endereco)
            zab.setUser(zab_usuario)
            zab.setPassword(zab_senha)
            if zab.login() == True:
                create_resp = zab.createPingTrigger(int(self.hostids), self.nome, self.endereco)
                if  create_resp:
                    jresp = json.loads(create_resp)
                    triggerids = int(jresp['triggerids'][0])
                    status   = Status.objects.get(label='ATIVO')
                    self.tentativa = 0
        except:
            return False

        #incluindo trigger no mysql
        with transaction.commit_manually():
            try:
                trigger = Trigger(nome=self.nome,
                    label=self.label,
                    tentativa=self.tentativa,
                    status=status,
                    host=host,
                    zabbix_id=triggerids, 
                    data_criacao=datetime.datetime.now())
                trigger.save()
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
                "Triggerids": triggerids
            }
            return retorno

