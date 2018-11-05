# -*- coding:utf-8 -*-
from django.http import HttpResponse
from api.models import ApiUsers,ApiLogs,ApiAction,ApiTipo
from lib.error import raiseError
import datetime,warnings,local

class Log(object):
    @staticmethod
    def saveAlog(request,alog=None,result=None,obs=None,referencia_id=None,action_nome=None,tipo_nome=None):
        warnings.filterwarnings("ignore")

        if not alog:
            api_key = request.GET.get("API_KEY","")

            try:
                user = ApiUsers.objects.using("log").get(api_key=api_key)
                alog = ApiLogs(user=user)
            except Exception,error:
                return raiseError(None,"auth_required",request,error)

        try:            
            alog.remote_addr = request.META.get("REMOTE_ADDR","")
            alog.path = request.META.get("PATH_INFO","")
            alog.get_params = dict(request.GET)
            alog.post_params = dict(request.POST)
            alog.usuario = request.GET.get("usuario","")

            if result:
                alog.result = result

            if obs:
                alog.obs = obs

            if referencia_id:
                alog.referencia_id = referencia_id

            if action_nome:
                if not action_nome == "listar":
                    try:
                        api_action = ApiAction.objects.using("log").get(nome=action_nome)
                    except Exception,error:
                        api_action = None

                elif action_nome == "listar":
                    if not local.SAVE_LOG_LIST:
                        alog.delete()

                    elif local.SAVE_LOG_LIST:
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

            alog.data_create = datetime.datetime.now()
            alog.save(using="log")

        except Exception,error:
            return raiseError(None,"auth_required",request,error)

        if alog and not result:
            return alog
