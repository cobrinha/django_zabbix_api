#!/usr/bin/env python
import os
import sys, traceback, json
import logging, logging.handlers
from daemon import runner
import time
import datetime
import requests

homeDir = os.getenv("HOME")
project_path = os.path.join(homeDir, 'azabbix/azabbix')
sys.path.append(project_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
from api.models import *
from api.zabbix import Zabbix
import local

zab = Zabbix()
zab.setHost("https://localhost/zabbix")
zab.setUser("Admin_user")
zab.setPassword("Admin_password")
if zab.login() == True:
    create_resp = zab.createUser("zezinho", "teste", local.ZABBIX_USRGRPID)
    if create_resp :
        jresp = json.loads(create_resp)
        userids = int(jresp['result']['userids'][0])
        print userids
    else:
        print create_resp
