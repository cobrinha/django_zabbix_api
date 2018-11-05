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

        api_obs = u"Listagem de Status"
        api_log_referencia_id = None
        api_log_action_nome = "listar"
        api_log_tipo_nome = "status"
        alog = Log.saveAlog(request)

        status_label   = request.GET.get('label')

        if not status_nome:
            try:
                retorno = []
                for item in Status.objects.all():
                    val = {}
                    val['nome'] = item.nome
                    val['label'] = item.label
                    val['data_criacao'] = item.data_criacao
                    retorno.append(val)
            except Exception,error:
                return raiseError(alog,"list_error", request, None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            try:
                status = Status.objects.get(nome=status_label)
                retorno = {
                    'nome' : status.nome,
                    'label' : status.label,
                    'status' : status.status.label
                }
            except Exception,error:
                return raiseError(alog,"list_error",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        return retorno

    def create(self,request):
        pass

class Add(BaseHandler):
    allowed_methods = ("GET",)

    def read(self,request):

        api_obs = u"Adição de Status"
        api_log_referencia_id = None
        api_log_action_nome = "criar"
        api_log_tipo_nome = "status"

        alog = Log.saveAlog(request)

        status_label = request.GET.get('label',None)

        if filter(lambda value:not value or value is None,[status_label]):
            return raiseError(alog,"param_missing",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            pass

        NAME_LENGTH = 10
        NAME_CHARS = "abcdefghjkmnpqrstuvwxyz23456789"
        nome_hash = User.objects.make_random_password(length=NAME_LENGTH,allowed_chars=NAME_CHARS)

        error_transaction = None

        with transaction.commit_manually():
            try:
                status = Status(nome=status_nome,
                    label=status_label,
                    data_criacao=datetime.datetime.now())
                status.save()

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

        api_log_referencia_id = status.id

        Log.saveAlog(request,alog,retorno,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        return retorno

    def create(self,request):
        pass

class Update(BaseHandler):
    allowed_methods = ("GET",)

    def read(self,request):

        api_obs = u"Edição de Status"

        api_log_referencia_id = None
        api_log_action_nome = "update"
        api_log_tipo_nome = "status"
 
        alog = Log.saveAlog(request)

        status_nome  = request.GET.get('nome',None)
        status_label    = request.GET.get('label',None)

        if filter(lambda value:not value or value is None,[status_nome, status_label]):
            return raiseError(alog,"param_missing",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            pass

        try:    
            status = Status.objects.get(nome=status_nome)
        except Exception, e:
            return raiseError(alog,"status_not_exist",request,e,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        error_transaction = None
        with transaction.commit_manually():
            try:
                if status_label:
                    status.label = status_label
                status.save()
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

        api_log_referencia_id = status.id

        Log.saveAlog(request,alog,retorno,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        return retorno

    def create(self,request):
        pass



