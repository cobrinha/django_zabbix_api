# -*- coding: utf-8 -*-
# importa bibliotecas piston
from piston.resource import Resource
from piston.handler import BaseHandler
from piston.utils import rc

# importa bibliotecas django
from django.db import transaction
from django.contrib.auth.models import User

# importa os models
from api.models import *

# importa lib local
from lib.log import Log
from lib.error import raiseError

# importa outras lib
import local,json,re,datetime,copy

#importa zabbix
from api.zabbix import Zabbix

class List(BaseHandler):
    allowed_methods = ("GET",)

    def read(self,request):
        api_obs = u"Listagem de Servidores"
        api_log_referencia_id = None
        api_log_action_nome = "listar"
        api_log_tipo_nome = "servidor"
        alog = Log.saveAlog(request)

        servidor_nome   = request.GET.get('nome')

        if not servidor_nome:
            try:
                retorno = []
                for item in Servidor.objects.all():
                    val = {}
                    val['status'] = item.status.label
                    val['nome'] = item.nome
                    val['endereco'] = item.endereco
                    val['label'] = item.label
                    val['data_criacao'] = item.data_criacao
                    retorno.append(val)
            except Exception,error:
                return raiseError(alog,"list_error", request, None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            try:
                servidor = Servidor.objects.get(nome=servidor_nome)
                retorno = {
                    'endereco' : servidor.endereco,
                    'nome' : servidor.nome,
                    'label' : servidor.label,
                    'status' : servidor.status.label,
                    'data_criacao' : servidor.data_criacao
                }
            except Exception,error:
                return raiseError(alog,"list_error",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        return retorno

    def create(self,request):
        pass

class Add(BaseHandler):
    allowed_methods = ("GET",)

    def read(self,request):

        api_obs = u"Adição de Servidor"
        api_log_referencia_id = None
        api_log_action_nome = "criar"
        api_log_tipo_nome = "servidor"

        alog = Log.saveAlog(request)

        NAME_LENGTH = 10
        NAME_CHARS = "abcdefghjkmnpqrstuvwxyz23456789"
        nome_hash = User.objects.make_random_password(length=NAME_LENGTH,allowed_chars=NAME_CHARS)

        servidor_nome           = str(nome_hash)
        servidor_endereco    = request.GET.get('endereco', None)
        servidor_label            = request.GET.get('label', None)
        servidor_status            = request.GET.get('status', None)

        if filter(lambda value:not value or value is None,[servidor_nome, servidor_endereco, servidor_label, servidor_status]):
            return raiseError(alog,"param_missing",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            pass

        nome = Servidor.objects.filter(nome=servidor_nome)

        if nome:
            return raiseError(alog, "server_name_exists",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            pass

        try:
            status = Status.objects.get(label=servidor_status)
        except Exception,error:
            return raiseError(alog, "status_not_exist",request,error,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        error_transaction = None

        with transaction.commit_manually():
            try:
                servidor = Servidor(nome=servidor_nome,
                    endereco=servidor_endereco,                    
                    status=status,                    
                    label=servidor_label,
                    data_criacao=datetime.datetime.now())
                servidor.save()

            except Exception,error:
                error_transaction = error
                transaction.rollback()

            else:
                transaction.commit()

        if error_transaction:
            return raiseError(alog,"error_in_transaction",request,error_transaction,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        retorno = {
            "Success":True
        }

        api_log_referencia_id = servidor.id

        Log.saveAlog(request,alog,retorno,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        return retorno

    def create(self,request):
        pass

class Update(BaseHandler):
    allowed_methods = ("GET",)

    def read(self,request):

        api_obs = u"Edição de servidor"

        api_log_referencia_id = None
        api_log_action_nome = "update"
        api_log_tipo_nome = "servidor"
 
        alog = Log.saveAlog(request)

        servidor_nome        = request.GET.get('nome',None)
        servidor_endereco    = request.GET.get('endereco',None)
        servidor_label       = request.GET.get('label',None)
        servidor_status      = request.GET.get('status',None)

        if filter(lambda value:not value or value is None,[servidor_nome]):
            return raiseError(alog,"param_missing",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            pass

        try:    
            servidor = Servidor.objects.get(nome=servidor_nome)
        except Exception, e:
            return raiseError(alog,"server_not_exist",request,e,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        error_transaction = None

        with transaction.commit_manually():
            try:

                if servidor_endereco:
                    servidor.endereco = servidor_endereco

                if servidor_label:
                    servidor.label = servidor_label

                if servidor_status:
                    try:
                        status = Status.objects.get(label=servidor_status)
                        servidor.status = status
                    except Exception,error:
                        return raiseError(alog, "status_not_exist",request,error,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

                servidor.save()

            except Exception,error:
                error_transaction = error
                transaction.rollback()

            else:
                transaction.commit()

        if error_transaction:
            return raiseError(alog,"error_in_transaction",request,error_transaction,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        retorno = {
            "Success":True
        }

        api_log_referencia_id = servidor.id

        Log.saveAlog(request,alog,retorno,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
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

        servidor_nome  = request.GET.get("nome",None)

        if filter(lambda value:not value or value is None,[servidor_nome]):
            return raiseError(alog,"param_missing",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            pass

        try:    
            servidor = Servidor.objects.get(nome=servidor_nome)
        except Exception, e:
            return raiseError(alog,"server_not_exist",request,e,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        error_transaction = None

        with transaction.commit_manually():
            try:
                status = Status.objects.get(label='INATIVO')
                if status:
                    servidor.status = status
                    servidor.save()
                else:
                    return raiseError(alog,"status_not_exist",request,e,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

            except Exception,error:
                error_transaction = error
                transaction.rollback()

            else:
                transaction.commit()

        if error_transaction:
            return raiseError(alog,"error_in_transaction",request,error_transaction,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        retorno = {
            "Success":True
        }
        api_log_referencia_id = servidor.id
        Log.saveAlog(request,alog,retorno,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        return retorno

    def create(self,request):
        pass

