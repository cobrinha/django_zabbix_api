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

class List(BaseHandler):
    allowed_methods = ("GET",)

    def read(self,request):
        api_obs = u"Listagem de Usuários"
        api_log_referencia_id = None
        api_log_action_nome = "listar"
        api_log_tipo_nome = "usuario"

        alog = Log.saveAlog(request)

        usuario_nome     = request.GET.get('nome')
        usuario_usuario  = request.GET.get('usuario')
        usuario_email     = request.GET.get('email')

        #listar com parametros
        if usuario_nome or usuario_usuario or usuario_email:
            try:
                usuario = Usuario.objects.filter(Q(nome=usuario_nome) | Q(usuario=usuario_usuario) | Q(email=usuario_email))
                retorno = {
                    'nome'        : usuario[0].nome,
                    'label'          : usuario[0].label,
                    'email'         : usuario[0].email,
                    'senha'        : usuario[0].senha,
                    'tentativa'  : usuario[0].tentativa,
                    'servidor'    : usuario[0].servidor.label,
                    'status'        : usuario[0].status.label
                }
            except Exception,error:
               return raiseError(alog,"list_error",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        #listar todos
        else:
            try:
                retorno = []
                for item in Usuario.objects.all():
                    val = {}
                    val['nome'] = item.nome
                    val['label'] = item.label
                    val['email'] = item.email
                    val['senha'] = item.senha
                    val['tentativa'] = item.tentativa
                    val['servidor'] = item.servidor.label
                    val['status'] = item.status.label
                    retorno.append(val)
            except Exception,error:
                return raiseError(alog,"list_error",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        return retorno
 
    def create(self,request):
        pass

class Add(BaseHandler):
    allowed_methods = ("GET",)

    def read(self,request):

        api_obs = u"Adição de usuário"
        api_log_referencia_id = None
        api_log_action_nome = "criar"
        api_log_tipo_nome = "usuario"

        alog = Log.saveAlog(request)

        #gerando nome
        NAME_LENGTH = 10
        NAME_CHARS = "abcdefghjkmnpqrstuvwxyz23456789"
        nome_hash = User.objects.make_random_password(length=NAME_LENGTH,allowed_chars=NAME_CHARS)

        usuario_nome          = str(nome_hash)        
        usuario_contrato     = request.GET.get("contrato")
        usuario_usuario       = request.GET.get("usuario")
        usuario_label            = request.GET.get("label")
        usuario_servidor       = request.GET.get("servidor")
        usuario_email           = request.GET.get("email")
        usuario_senha          = request.GET.get("senha")

        #validando parametros   
        if filter(lambda value:not value or value is None,[usuario_label, usuario_usuario, usuario_email, usuario_senha,  usuario_contrato, usuario_servidor]):
            return raiseError(alog,"param_missing",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        #buscando id do servidor
        try:
            servidor   = Servidor.objects.get(nome=usuario_servidor)
        except  ObjectDoesNotExist:
            return raiseError(alog,"server_not_exist",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome) 
        else:
            usuario_servidor = servidor.id
     
        usuario = Usuario.objects.filter(usuario=usuario_usuario)
        email   = Usuario.objects.filter(email=usuario_email)

        #verificando se usuario ou e-mail existem
        if usuario:
            return raiseError(alog,"user_exist",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        elif email:
            return raiseError(alog,"email_exist",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        error_transaction = None

        # valores caso nao consiga incluir no Zabbix
        usuario_tentativa = 1
        status   = Status.objects.get(label='INCLUIR')
        userids = 0

        # tentando incluir no Zabbix
        try:
            zab_usuario    = local.SERVER_ZABBIX[servidor.nome]['usuario']
            zab_senha       = local.SERVER_ZABBIX[servidor.nome]['senha']
            zab = Zabbix()
            zab.setHost(servidor.endereco)
            zab.setUser(zab_usuario)
            zab.setPassword(zab_senha)
            if zab.login() == True:
                create_resp = zab.createUser(usuario_email, usuario_senha, local.ZABBIX_USRGRPID)
                if create_resp :
                    jresp = json.loads(create_resp)
                    userids = int(jresp['result']['userids'][0])
                    status   = Status.objects.get(label='ATIVO')
                    usuario_tentativa = 0
        except:
            pass

        #incluindo
        with transaction.commit_manually():
            try:
                usuario = Usuario(
                    nome=usuario_nome,
                    usuario=usuario_usuario,
                    label=usuario_label,
                    servidor =servidor,
                    email=usuario_email,
                    zabbix_id=userids,
                    senha=usuario_senha,
                    contrato=usuario_contrato,
                    tentativa=usuario_tentativa,
                    status =status, 
                    data_criacao=datetime.datetime.now())
                usuario.save()

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

        api_log_referencia_id = usuario.id

        Log.saveAlog(request,alog,retorno,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        return retorno

    def create(self,request):
        pass

class Update(BaseHandler):
    allowed_methods = ("GET",)

    def read(self,request):

        api_obs = u"Edicao de usuário"

        api_log_referencia_id = None
        api_log_action_nome = "update"
        api_log_tipo_nome = "usuario"
 
        alog = Log.saveAlog(request)

        usuario_servidor       = request.GET.get("servidor")
        usuario_label            = request.GET.get("label")
        usuario_nome           = request.GET.get("nome")
        usuario_usuario        = request.GET.get("usuario")
        usuario_email            = request.GET.get("email")
        usuario_senha           = request.GET.get("senha")
        usuario_status           = request.GET.get("status")

        #valida usuario_nome
        if filter(lambda value:not value or value is None,[usuario_nome]):
            return raiseError(alog,"param_missing",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            pass

        try:    
            usuario = Usuario.objects.get(nome=usuario_nome)
        except Exception, e:
            return raiseError(alog,"user_not_exist",request,e,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        error_transaction = None

        status   = Status.objects.get(label=usuario_status)
        if status:
             usuario_status = status.id
        else:
            return raiseError(alog,"status_not_exist",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        with transaction.commit_manually():
            try:
                if usuario_senha:
                    usuario.senha = usuario_senha
                if usuario_label:
                    usuario.label = usuario_label
                if usuario_usuario:
                    usuario.usuario = usuario_usuario
                if usuario_email:
                    usuario.email = usuario_email
                if usuario_servidor:
                    servidor   = Servidor.objects.get(nome=usuario_servidor)
                    if servidor:
                         usuario.servidor = servidor.id
                    else:
                        return raiseError(alog,"server_not_exist",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
                if usuario_status:
                    status   = Status.objects.get(label=usuario_status)
                    if status:
                         usuario.status = status.id
                    else:
                        return raiseError(alog,"status_not_exist",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

                usuario.save()

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

        api_log_referencia_id = usuario.id

        Log.saveAlog(request,alog,retorno,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        return retorno

    def create(self,request):
        pass

class Delete(BaseHandler):
    allowed_methods = ("GET",)

    def read(self,request):

        api_obs = u"Exclusão de usuário"

        api_log_referencia_id = None
        api_log_action_nome = "delete"
        api_log_tipo_nome = "usuario"
 
        alog = Log.saveAlog(request)

        usuario_usuario = request.GET.get("usuario",None)

        if filter(lambda value:not value or value is None,[usuario_usuario]):
            return raiseError(alog,"param_missing",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        else:
            pass

        try:    
            usuario = Usuario.objects.get(usuario=usuario_usuario)
        except Exception, e:
            return raiseError(alog,"user_not_exist",request,e,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

        error_transaction = None

        with transaction.commit_manually():
            try:
                status   = Status.objects.get(label='INATIVO')
                if status:
                     usuario.status = status.id
                else:
                    return raiseError(alog,"status_not_exist",request,None,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)

                usuario.save()

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

        api_log_referencia_id = usuario.id

        Log.saveAlog(request,alog,retorno,api_obs,api_log_referencia_id,api_log_action_nome,api_log_tipo_nome)
        return retorno

    def create(self,request):
        pass

