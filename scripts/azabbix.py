#!/usr/bin/env python
import os
import sys, traceback
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

class AZabbixDaemon():

    def __init__(self, logger):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  local.PID_PATH
        self.pidfile_timeout = 5
        self.logger = logger
        self.runningDaemon = True

    def run(self):
        self.logger.info("--- starting daemon ---")
        lastCheck = datetime.datetime.now() - datetime.timedelta(days=1)

        #dummy call - ???
        datetime.datetime.strptime('2017-02-06', '%Y-%m-%d')

        try:
            while self.runningDaemon:# = True
                now = datetime.datetime.now()
                if now > lastCheck + datetime.timedelta(seconds=30):#(seconds=30):#
                    #aqui o codigo a ser executado a cada loop
                    self.incluirUsuario()
                time.sleep(10)
        except:
            self.logger.error('ending of main thread', exc_info=True)

        self.logger.info("--- ending of daemon ---")

    def __del__(self):
        pass

    def logScript():
        pass

    def incluirUsuario():
        api_obs = u"Incluir Usuario"
        api_log_referencia_id = None
        api_log_action_nome = "add"
        api_log_tipo_nome = "script"
        alog = "script"

        usuario = Usuario.objects.filter(status__label = 'incluir')
        status   = Status.objects.get(label='ativo')
        if status:
             usuario_status = status.id

        for aUsuario in usuario:
            servidor    = aUsuario.servidor.nome
            email        = aUsuario.email
            senha       = aUsuario.senha
            userids     = 0
            zab_endereco = aUsuario.servidor.endereco
            zab_usuario    = local.SERVER_ZABBIX[servidor]['usuario']
            zab_senha       = local.SERVER_ZABBIX[servidor]['senha']
            zab = Zabbix()
            zab.setHost(zab_endereco)
            zab.setUser(zab_usuario)
            zab.setPassword(zab_senha)
            if zab.login() == True:
                create_resp = zab.createUser(email, senha, local.ZABBIX_USRGRPID)
                if create_resp :
                    jresp = json.loads(create_resp)
                    userids = int(jresp['result']['userids'][0])

            with transaction.commit_manually():
                try:
                    if userids != 0:
                        print '1'
                        usuario.status = usuario_status
                        usuario.zabbix_id = userids
                    else:
                        print '0'
                        usuario.tentativa = usuario.tentativa + 1
                    usuario.save()
                except:
                    pass

        return True

logger = logging.getLogger("")
logger.setLevel(logging.INFO)#logging.INFO
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.handlers.TimedRotatingFileHandler(local.LOG_PATH, when='midnight', backupCount=0)
handler.setFormatter(formatter)
logger.addHandler(handler)
loggerEx = logging.getLogger("daemon")
loggerEx.setLevel(logging.INFO)#logging.DEBUG)

try:
    app = AZabbixDaemon(loggerEx)
    daemon_runner = runner.DaemonRunner(app)
    #This ensures that the logger file handle does not get closed during daemonization
    daemon_runner.daemon_context.files_preserve=[handler.stream]
    logger.info( 'deamon action = ' + daemon_runner.action )
    daemon_runner.do_action()
except runner.DaemonRunnerError, e:
    print str(e) + ' - finalizando coletor daemon'
    logger.error('Erro no daemon, finalizando', exc_info=True)
except Exception, e:
    logger.error('Erro no daemon, finalizando', exc_info=True)


