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

class ZabbixItem:

    def __init__(self,  nome, endereco, hostids="0"):
        #incluindo item para o host
        self.nome             = nome
        self.label               = endereco
        self.endereco      = endereco
        self.hostids          = hostids
       
    def Add(self, request):
        api_obs = u"Inclusao de item no Zabbix"
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

        # valores caso nao consiga incluir item no Zabbix
        error_transaction = None
        self.tentativa = 1
        status   = Status.objects.get(label='INCLUIR')
        itemids = 0

        # tentando incluir item no Zabbix
        try:
            zab_usuario    = local.SERVER_ZABBIX[servidor.nome]['usuario']
            zab_senha       = local.SERVER_ZABBIX[servidor.nome]['senha']
            zab = Zabbix()
            zab.setHost(servidor.endereco)
            zab.setUser(zab_usuario)
            zab.setPassword(zab_senha)

            if zab.login() == True:
                interfaceIds = zab.getHostInterface(self.hostids)
                for a in interfaceIds:
                    if str(a['hostid']==self.hostids):
                        interface_id  = a['interfaceid']

                create_resp = zab.createPingItem(self.label, int(self.hostids), int(interface_id))
                if create_resp :
                    jresp = json.loads(create_resp)
                    itemids = int(jresp['itemids'][0])
                    status   = Status.objects.get(label='ATIVO')
                    self.tentativa = 0
        except:
            pass

        #incluindo item no mysql
        with transaction.commit_manually():
            try:
                item = Item(nome=self.nome,
                    label=self.label,
                    tentativa=self.tentativa,
                    status=status,
                    host=host,
                    zabbix_id=itemids, 
                    data_criacao=datetime.datetime.now())
                item.save()
            except Exception,error:
                error_transaction = error
                transaction.rollback()
            else:
                transaction.commit()
    
        #retornando da inclusao
        if error_transaction:
                return raiseError(alog,"error_in_transaction",request,error_transaction,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
                #retornando da inclusao
                retorno = {
                    "Success":True,
                    "Nome": self.nome,
                    "Endereco": self.endereco,
                    "Itemids": itemids
                }
                return retorno



