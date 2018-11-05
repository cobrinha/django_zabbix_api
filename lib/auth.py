# -*- coding:utf-8 -*-
from django.http import HttpResponse
from api.models import ApiUsers,ApiLogs
from lib.error import raiseError

class ApiKeyAuthentication(object):
    def is_authenticated(self,request):
        auth_string = request.GET.get("API_KEY",None)

        try:
            ApiUsers.objects.using("log").get(api_key=auth_string)
        except Exception,error:
           return False

        return True

    def challenge(self):
        resp = HttpResponse("Authentication Required")
        resp["WWW-Authenticate"] = "Key Based Authentication"
        resp.status_code = 401
        return resp