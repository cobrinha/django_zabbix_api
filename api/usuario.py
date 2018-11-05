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

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class ZabbixUsuario:
    def __init__(self, nome, endereco, contrato, email, grupo_id=0):
        #definindo parametros de usuario
        self.usuario_nome          = nome       
        self.usuario_endereco   = endereco
        self.usuario_contrato    = contrato
        self.usuario_usuario       = nome
        self.usuario_label            = nome
        self.usuario_email           = email
        self.usuario_senha          = id_generator()
        self.usuario_grupo_id    = int(grupo_id)

    def Add(self, request):
        api_obs = u"Inclusao de usuario no Zabbix"
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
        usuario = Usuario.objects.filter(usuario=self.usuario_usuario)
        email   = Usuario.objects.filter(email=self.usuario_email)

        #verificando se usuario ou e-mail existem
        if usuario:
            return raiseError(alog,"user_exist",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        elif email:
            return raiseError(alog,"email_exist",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        error_transaction = None

        # valores caso nao consiga incluir usuario no Zabbix
        usuario_tentativa = 1
        status   = Status.objects.get(label='INCLUIR')
        userids = 0

        # tentando incluir usuario no Zabbix
        try:
            zab_usuario    = local.SERVER_ZABBIX[servidor.nome]['usuario']
            zab_senha       = local.SERVER_ZABBIX[servidor.nome]['senha']
            zab = Zabbix()
            zab.setHost(servidor.endereco)
            zab.setUser(zab_usuario)
            zab.setPassword(zab_senha)
            if zab.login() == True:
                create_resp = zab.createUser(self.usuario_nome, self.usuario_senha, self.usuario_grupo_id)
                if create_resp :
                    jresp = json.loads(create_resp)
                    userids = int(jresp['result']['userids'][0])
                    status   = Status.objects.get(label='ATIVO')
                    zab.createMedia(userids, self.usuario_email)
                    usuario_tentativa = 0
        except:
            pass

        #incluindo usuario no mysql
        with transaction.commit_manually():
            try:
                usuario = Usuario(
                    nome=self.usuario_nome,
                    usuario=self.usuario_usuario,
                    label=self.usuario_label,
                    servidor =servidor,
                    email=self.usuario_email,
                    zabbix_id=userids,
                    zabbix_grupo_id=self.usuario_grupo_id,
                    contrato=self.usuario_contrato,
                    tentativa=usuario_tentativa,
                    status =status, 
                    data_criacao=datetime.datetime.now())
                usuario.save()
            except Exception,error:
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
                "Userids": userids,
                "Nome": self.usuario_nome,
                "Email": self.usuario_email,
                "Label": self.usuario_label,
                "Endereco": self.usuario_endereco,
                "Usuario": self.usuario_usuario,
                "Senha": self.usuario_senha,
                "Servidor": servidor.nome
            }

            return retorno






