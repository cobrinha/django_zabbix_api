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

#importa classes
from api.usuario import ZabbixUsuario
from api.host import ZabbixHost
from api.item import ZabbixItem
from api.trigger import ZabbixTrigger
from api.grupo_usuario import ZabbixGrupoUsuario
from api.grupo_host import ZabbixGrupoHost
from api.massadd import ZabbixMassAdd
from api.action import ZabbixAction
from api.utils import ZabbixUtils

import string
import random

class DbException(Exception):
    pass

class Add(BaseHandler):
    ### URL PARA INCLUSAO
    ### myhost.com/api/host_teste/add/?API_KEY=12345&endereco=179.57.147.200&contrato=CAN54321&email=teste@gmail.com
    allowed_methods = ("GET",)

    def read(self,request):
        api_obs = u"Inclusao de icmpping no Zabbix"
        api_log_referencia_id = None
        api_log_action_nome = "criar"
        api_log_tipo_nome = "zab"

        alog = Log.saveAlog(request)

        NAME_LENGTH = 10
        NAME_CHARS = "abcdefghjkmnpqrstuvwxyz23456789"
        nome_hash = User.objects.make_random_password(length=NAME_LENGTH,allowed_chars=NAME_CHARS)

        #recebendo parametros
        nome            = str(nome_hash)
        endereco     = request.GET.get('endereco', None)
        contrato       = request.GET.get('contrato', None)
        email             = request.GET.get('email', None)  

        #verificando parametros
        if filter(lambda value:not value or value is None,[nome, endereco, contrato, email]):
            return raiseError(alog,"param_missing",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            pass

        #validação das entradas de dados
        oUtils = ZabbixUtils()
        if oUtils.validarEmail(email)==False:
            return raiseError(alog,"invalid_email",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        if oUtils.validarIP(endereco)==False:
            return raiseError(alog,"invalid_ip",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        
        if oUtils.validarContrato(contrato)==False:
            return raiseError(alog,"invalid_contract",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        #grupo de usuarios
        oGrupoUsuario  =   ZabbixGrupoUsuario(nome)
        dGrupoUsuario =  oGrupoUsuario.Add(request)
        try:
            if  dGrupoUsuario.get('Success', False)!= True:
                if dGrupoUsuario.get('Error', False)== 'ZabbixError':
                    return raiseError(alog,"create_group_user_fail",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
                else:
                    return str(dGrupoUsuario)
            else:
                GrupoNome = dGrupoUsuario.get('Nome', False)
                UserGroupIds = dGrupoUsuario.get('UserGroupIds', False)
        except:
                return raiseError(alog,"create_group_user_fail",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        #usuario
        oUsuario  =   ZabbixUsuario(nome, endereco, contrato, email, UserGroupIds)
        dUsuario = oUsuario.Add(request)
        try:
            if  dUsuario.get('Success', False)!= True:
                return str(dUsuario)
            else:
                Nome = dUsuario.get('Nome', False)
                Userids =dUsuario.get('Userids', False)
                Label = dUsuario.get('Label', False)
                Endereco = dUsuario.get('Endereco', False)
                Usuario = dUsuario.get('Usuario', False)
                Email = dUsuario.get('Email', False)
                Senha = dUsuario.get('Senha', False )
                Servidor = dUsuario.get('Servidor', False)
        except:
            return raiseError(alog,"create_user_fail",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
          
        #grupo de hosts
        oGrupoHost  =   ZabbixGrupoHost(nome, Servidor)
        dGrupoHost =  oGrupoHost.Add(request)
        try:
            if  dGrupoHost.get('Success', False) != True:
                return str(dGrupoHost)
            else:
                HostGrupoNome = str(dGrupoHost['Nome'] )
                HostGroupIds = str(dGrupoHost['HostGroupIds'] )
        except:
            return raiseError(alog,"create_group_host_fail",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        #host
        oHost  =   ZabbixHost(Nome, Usuario, Email, Label, Endereco, HostGroupIds, 'IP', '0')
        dHost = oHost.Add(request)
        if  dHost.get('Success', False)  != True:
            return str(dHost)
            #return raiseError(alog,"create_host_fail",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
             Nome = str(dHost['Nome'] )
             Endereco = str(dHost['Endereco'] )
             Hostids = dHost['Hostids']     

        #item
        oItem  =   ZabbixItem(Nome, Endereco,  Hostids)
        dItem = oItem.Add(request)
        if  dItem.get('Success', False) != True:
            return str(dItem)
            #return raiseError(alog,"create_item_fail",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
             Nome = str(dItem['Nome'] )
             Endereco = str(dItem['Endereco'] )
             Itemids = dItem['Itemids'] 

        #Trigger
        oTrigger  =   ZabbixTrigger(Nome, Endereco, str(Hostids))
        dTrigger = oTrigger.Add(request)
        if  dTrigger.get('Success', False) != True:
            return str(dTrigger)
            #return raiseError(alog,"create_trigger_fail",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:   
            Triggerids = dTrigger['Triggerids'] 
       
        #MassAdd
        oMassAdd =  ZabbixMassAdd(UserGroupIds, HostGroupIds)
        dMassAdd =  oMassAdd.Add(request)
        if  dMassAdd.get('Success', False) != True:
            return str(dMassAdd)
            #return raiseError(alog,"create_group_user_fail",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            MassAddIds = dMassAdd['UserGroupIds'] 

        #Action
        oAction  =   ZabbixAction(Nome, UserGroupIds, HostGroupIds)
        dAction  = oAction.Add(request)
        if  dAction.get('Success', False) != True:
            return str(dAction)
            #return raiseError(alog,"create_group_user_fail",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            ActionIds = dAction['Actionids'] 
            retorno = {
                        'Success' : True, 
                        'Email': Email,
                        'Nome': Nome,    
                        'Senha':  Senha, 
                        'Userids': Userids,  
                        'UserGroupIds': UserGroupIds, 
                        'Hostids':  Hostids, 
                        'HostGroupIds': HostGroupIds,        
                        'Itemids': Itemids, 
                        'Triggerids': Triggerids, 
                        'MassAddIds': MassAddIds,                      
                        'ActionIds': ActionIds
            } 
            return retorno

    def create(self,request):
        pass

class Delete(BaseHandler):
    allowed_methods = ("GET",)

    def read(self,request):
        api_obs = u"Exclusão de servidor"
        api_log_referencia_id = None
        api_log_action_nome = "delete"
        api_log_tipo_nome = "servidor"
        alog = Log.saveAlog(request)

        if filter(lambda value:not value or value is None,[servidor_nome]):
            return raiseError(alog,"param_missing",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            pass

        retorno = {
            "Success":True
        }
        api_log_referencia_id = servidor.id
        Log.saveAlog(request,alog,retorno,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        return retorno

    def create(self,request):
        pass

