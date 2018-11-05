# -*- coding:utf-8 -*-
from django.http import HttpResponse
from api.models import ApiUsers,ApiLogs,ApiErrors,ApiAction,ApiTipo
import warnings

def raiseError(alog,code,request,errorException=None,obs=None,referencia_id=None,action_nome=None,tipo_nome=None):
    warnings.filterwarnings("ignore")

    try:
        error = ApiErrors.objects.using("log").get(code=code)
        alog.error = error
        code = error.code
        msg = error.message+"(codigo="+unicode(1000+error.id)+")"
    except Exception,error:
        msg = "Erro nao encontrado"
        code = "00x0"

    try:
        alog.remote_addr = request.META.get("REMOTE_ADDR","")
        alog.path = request.META.get("PATH_INFO","")
        alog.get_params = request.GET
        alog.post_params = request.POST

        if errorException:
            alog.result = errorException

        if obs:
            alog.obs = obs

        if referencia_id:
            alog.referencia_id = referencia_id

        if action_nome:
            try:
                api_action = ApiAction.objects.using("log").get(nome=action_nome)
            except Exception,error:
                api_action = None

            alog.action = api_action

        if tipo_nome:
            try:
                api_tipo = ApiTipo.objects.using("log").get(nome=tipo_nome)
            except Exception,error:
                api_tipo = None

            alog.tipo = api_tipo

        alog.save(using="log")
    except Exception,error:
        msg = msg + ' - ' + str(error)

    return {
        "Success":False,
        "ErrorCode":code,
        "Message":msg,
        "ErrorException":str(errorException)
    }