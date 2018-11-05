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

class ZabbixHost:
    def __init__(self,  nome, usuario, email,  label, endereco,  grupo_id, tipo='IP', porta='0'):
        #definindo parametros do host
        self.nome              = nome
        self.usuario          = usuario
        self.email              = email
        self.label               = label
        self.endereco      = endereco
        self.grupo_id       = grupo_id
        self.tipo                 = 'IP'
        self.porta              = '0'

    def Add(self, request):
        api_obs = u"Inclusao de host no Zabbix"
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

        usuario = Usuario.objects.filter(usuario=self.usuario)
        email   = Usuario.objects.filter(email=self.email)

        #incluindo host, buscando id do usuario
        try:
            usuario   = Usuario.objects.get(nome=self.nome)
        except  ObjectDoesNotExist:
            return raiseError(alog,"user_not_exist",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome) 
        else:
            host_usuario  = usuario.id
            usuario_servidor = usuario.servidor_id
            host_servidor_endereco = servidor.endereco
         
        #verificando porta e endereço iguais
        endereco    = Host.objects.filter(endereco=self.endereco)
        porta           = Host.objects.filter(porta=self.porta)
        if endereco and porta:
            return raiseError(alog,"host_same_address_port",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            pass
       
        # valores caso nao consiga incluir no Zabbix
        error_transaction = None
        self.tentativa = 1
        status   = Status.objects.get(label='INCLUIR')
        hostids = 0

        # tentando incluir host no Zabbix
        try:
            zab_usuario    = local.SERVER_ZABBIX[servidor.nome]['usuario']
            zab_senha       = local.SERVER_ZABBIX[servidor.nome]['senha']
            zab = Zabbix()
            zab.setHost(servidor.endereco)
            zab.setUser(zab_usuario)
            zab.setPassword(zab_senha)

            if zab.login() == True:
                useip = 1
                dns = ''
                interfaces =   { 
                    "type":  1, 
                    "main":  1, 
                    "useip":  useip, 
                    "ip":  self.endereco, 
                    "dns":  dns, 
                    "port":  self.porta
                }
                groups = {
                    "groupid" :  self.grupo_id
                }
                create_resp = zab.createHost(self.nome, interfaces, groups)
                if create_resp :
                    jresp = json.loads(create_resp)
                    hostids = int(jresp['hostids'][0])
                    status   = Status.objects.get(label='ATIVO')
                    self.tentativa = 0
        except Exception, error:
            pass

        #incluindo host no mysql
        with transaction.commit_manually():
            try:
                host = Host(nome=self.nome,
                    usuario=usuario,
                    endereco=self.endereco,
                    tipo=self.tipo,
                    label=self.nome,
                    porta=self.porta,
                    tentativa=self.tentativa,
                    status=status,
                    zabbix_id=hostids, 
                    data_criacao=datetime.datetime.now())
                host.save()
            except Exception, error:
                error_transaction = error
                transaction.rollback()
            else:
                transaction.commit()

        #retornando da inclusao
        if error_transaction:
            return raiseError(alog,"error_in_transaction",request,error_transaction,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            retorno = {
                "Success":True,
                "Hostids" : hostids,
                "Nome": self.nome,
                "Endereco": self.endereco
            }
            return retorno

